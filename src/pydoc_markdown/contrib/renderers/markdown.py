# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from __future__ import annotations

import dataclasses
import io
import re
import sys
import typing as t
from pathlib import Path

import docspec
from docspec_python import format_arglist
from yapf.yapflib.yapf_api import FormatCode  # type: ignore[import]

from pydoc_markdown.interfaces import (
    Context,
    Renderer,
    Resolver,
    ResolverV2,
    SingleObjectRenderer,
    SinglePageRenderer,
    SourceLinker,
)
from pydoc_markdown.util.docspec import ApiSuite, format_function_signature, is_method
from pydoc_markdown.util.misc import escape_except_blockquotes


def dotted_name(obj: docspec.ApiObject) -> str:
    return ".".join(x.name for x in obj.path)


_REFERENCE_DEFINITION_START_RE = re.compile(r"^ {0,3}\[")
_FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*?)(?:\r?\n)?$")
_LIST_MARKER_RE = re.compile(r"(?:[-+*]|\d{1,9}[.)])(?:[ \t]+|$)")
_HTML_BLOCK_RE = re.compile(
    r"(?i)^ {0,3}</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|"
    r"details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|"
    r"hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|section|"
    r"summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul)(?:[ \t]|/?>|$)"
)
_HTML_TAG_ONLY_RE = re.compile(r"(?i)^ {0,3}</?[a-z][^>]*>[ \t]*$")
_INLINE_HTML_TAG_RE = re.compile(
    r"(?ix)(?:"
    r"</[a-z][a-z0-9-]*[ \t\r\n]*>"
    r"|<[a-z][a-z0-9-]*"
    r"(?:[ \t\r\n]+[a-z_:][a-z0-9_.:-]*"
    r"(?:[ \t\r\n]*=[ \t\r\n]*(?:[^ \t\r\n\"'=<>`]+|'[^']*'|\"[^\"]*\"))?)*"
    r"[ \t\r\n]*/?>"
    r")"
)
_INLINE_RAW_HTML_RE = re.compile(
    r"(?:<!--(?:[^-]|-(?!-))*-->|<\?.*?\?>|<!\[CDATA\[.*?\]\]>|<![A-Z][^>]*>)",
    re.DOTALL,
)
_URI_AUTOLINK_RE = re.compile(r"<[a-z][a-z0-9+.-]{1,31}:[^\s<>]*>", re.IGNORECASE)
_ESCAPABLE_PUNCTUATION_RE = re.compile(r"[!-/:-@\[-`{-~]")


@dataclasses.dataclass
class _ReferenceUsage:
    start: int
    end: int
    append: bool = False


@dataclasses.dataclass
class _DocstringReferences:
    obj: docspec.ApiObject
    content: str
    definitions: t.Dict[str, t.List[t.Tuple[int, int]]] = dataclasses.field(default_factory=dict)
    links: t.Dict[str, t.List[_ReferenceUsage]] = dataclasses.field(default_factory=dict)


def _normalize_reference_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def _is_escaped(text: str, offset: int) -> bool:
    backslashes = 0
    offset -= 1
    while offset >= 0 and text[offset] == "\\":
        backslashes += 1
        offset -= 1
    return backslashes % 2 == 1


def _strip_blockquote_prefix(line: str) -> str:
    """Strips Markdown blockquote markers, retaining other container indentation."""

    offset = 0
    while True:
        start = offset
        spaces = 0
        while offset < len(line) and line[offset] == " " and spaces < 3:
            offset += 1
            spaces += 1
        if offset >= len(line) or line[offset] != ">":
            return line[start:]
        offset += 1
        if offset < len(line) and line[offset] in " \t":
            offset += 1


def _blockquote_depth(line: str) -> int:
    """Returns the number of leading Markdown blockquote containers."""

    depth = 0
    while True:
        offset = 0
        while offset < len(line) and line[offset] == " " and offset < 3:
            offset += 1
        if offset >= len(line) or line[offset] != ">":
            return depth
        depth += 1
        line = line[offset + 1 :]
        if line.startswith((" ", "\t")):
            line = line[1:]


def _strip_container_prefix(line: str) -> str:
    """Strips nested blockquote and one-line list container markers."""

    while True:
        stripped = _strip_blockquote_prefix(line)
        if stripped != line:
            line = stripped
            continue
        offset = 0
        while offset < len(line) and line[offset] == " " and offset < 3:
            offset += 1
        match = _LIST_MARKER_RE.match(line, offset)
        if not match:
            return line
        line = line[match.end() :]


def _strip_indent(line: str, width: int) -> str:
    """Strips up to *width* columns of container indentation from a line."""

    offset = 0
    column = 0
    while offset < len(line) and column < width and line[offset] in " \t":
        if line[offset] == " ":
            column += 1
        else:
            column += 4 - column % 4
        offset += 1
    return line[offset:] if column >= width else line


def _leading_indent(line: str) -> int:
    width = 0
    for char in line:
        if char == " ":
            width += 1
        elif char == "\t":
            width += 4 - width % 4
        else:
            break
    return width


def _visual_width(text: str) -> int:
    """Returns the number of Markdown columns occupied by *text*."""

    width = 0
    for char in text:
        width += 4 - width % 4 if char == "\t" else 1
    return width


def _list_content_indent(line: str) -> t.Optional[int]:
    """Returns the absolute indentation where a list item's content begins."""

    offset = 0
    while offset < len(line) and line[offset] == " " and offset < 3:
        offset += 1
    match = _LIST_MARKER_RE.match(line, offset)
    return _visual_width(line[: match.end()]) if match else None


def _reference_definition_end(text: str, colon: int, footnote: bool = False) -> t.Optional[int]:
    """Validates a reference definition and returns the end of its definition span."""

    line_end = len(text)
    for newline in (text.find("\n", colon + 1), text.find("\r", colon + 1)):
        if newline >= 0:
            line_end = min(line_end, newline)

    offset = colon + 1
    while offset < line_end and text[offset] in " \t":
        offset += 1
    if offset >= line_end:
        if not footnote:
            return None
        next_start = line_end
        if text.startswith("\r\n", next_start):
            next_start += 2
        elif next_start < len(text) and text[next_start] in "\r\n":
            next_start += 1
        else:
            return None
        next_end = len(text)
        for newline in (text.find("\n", next_start), text.find("\r", next_start)):
            if newline >= 0:
                next_end = min(next_end, newline)
        definition_start = max(text.rfind("\n", 0, colon), text.rfind("\r", 0, colon)) + 1
        definition_line = text[definition_start:line_end]
        continuation_line = text[next_start:next_end]
        if _blockquote_depth(definition_line) != _blockquote_depth(continuation_line):
            return None
        definition_content = _strip_blockquote_prefix(definition_line)
        continuation_content = _strip_blockquote_prefix(continuation_line)
        list_indent = _list_content_indent(definition_content) or 0
        if _leading_indent(continuation_content) < list_indent + 4 or not continuation_content.strip():
            return None
        return next_end
    if footnote:
        return line_end

    if text[offset] == "<":
        destination_start = offset + 1
        offset = destination_start
        while offset < line_end and (text[offset] != ">" or _is_escaped(text, offset)):
            offset += 1
        if offset >= line_end or offset == destination_start:
            return None
        offset += 1
    else:
        destination_start = offset
        depth = 0
        while offset < line_end and (not text[offset].isspace() or depth):
            if text[offset] == "\\" and offset + 1 < line_end and _ESCAPABLE_PUNCTUATION_RE.fullmatch(text[offset + 1]):
                offset += 2
                continue
            if text[offset] == "(":
                depth += 1
            elif text[offset] == ")":
                if depth == 0:
                    break
                depth -= 1
            offset += 1
        if offset == destination_start or depth:
            return None

    while offset < line_end and text[offset] in " \t":
        offset += 1
    if offset == line_end:
        next_start = line_end
        if text.startswith("\r\n", next_start):
            next_start += 2
        elif next_start < len(text) and text[next_start] in "\r\n":
            next_start += 1
        else:
            return line_end

        next_end = len(text)
        for newline in (text.find("\n", next_start), text.find("\r", next_start)):
            if newline >= 0:
                next_end = min(next_end, newline)
        definition_start = max(text.rfind("\n", 0, colon), text.rfind("\r", 0, colon)) + 1
        definition_line = text[definition_start:line_end]
        continuation_line = text[next_start:next_end]
        definition_quotes = _blockquote_depth(definition_line)
        continuation_quotes = _blockquote_depth(continuation_line)
        definition_content = _strip_blockquote_prefix(definition_line)
        continuation_content = _strip_blockquote_prefix(continuation_line)
        definition_list_indent = _list_content_indent(definition_content)
        continuation_in_same_list = (
            _list_content_indent(continuation_content) is None
            if definition_list_indent is None
            else _leading_indent(continuation_content) >= definition_list_indent
        )
        if definition_quotes != continuation_quotes or not continuation_in_same_list:
            return line_end

        continuation = _strip_container_prefix(continuation_line)
        continuation_offset = next_end - len(continuation)
        title_match = re.match(r" {0,3}([\"'(])", continuation)
        if not title_match:
            return line_end
        offset = continuation_offset + title_match.end() - 1
        line_end = next_end

    opener = text[offset]
    closer = {'"': '"', "'": "'", "(": ")"}.get(opener)
    if closer is None:
        return None
    offset += 1
    while offset < line_end and (text[offset] != closer or _is_escaped(text, offset)):
        offset += 1
    if offset >= line_end:
        return None
    offset += 1
    while offset < line_end and text[offset] in " \t":
        offset += 1
    return line_end if offset == line_end else None


def _mask_html_tags(mask: bytearray, text: str, start: int, end: int) -> None:
    """Masks inline HTML and URI autolinks so their brackets are not treated as links."""

    offset = start
    while offset < end:
        opening = text.find("<", offset, end)
        if opening < 0:
            return
        if mask[opening]:
            offset = opening + 1
            continue
        raw_html = _INLINE_RAW_HTML_RE.match(text, opening, end)
        if raw_html:
            closing = raw_html.end()
            if not any(mask[opening:closing]):
                mask[opening:closing] = b"\1" * (closing - opening)
            offset = closing
            continue
        if opening + 1 >= end or text[opening + 1] not in "!?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
            offset = opening + 1
            continue
        autolink_closing = text.find(">", opening + 1, end)
        if autolink_closing >= 0 and _URI_AUTOLINK_RE.fullmatch(text[opening : autolink_closing + 1]):
            autolink_closing += 1
            mask[opening:autolink_closing] = b"\1" * (autolink_closing - opening)
            offset = autolink_closing
            continue
        quote: t.Optional[str] = None
        closing = opening + 1
        while closing < end:
            char = text[closing]
            if quote:
                if char == quote:
                    quote = None
            elif char in "\"'":
                quote = char
            elif char == ">":
                closing += 1
                if _INLINE_HTML_TAG_RE.fullmatch(text[opening:closing]):
                    mask[opening:closing] = b"\1" * (closing - opening)
                    offset = closing
                    break
                offset = opening + 1
                break
            closing += 1
        else:
            return


def _markdown_protected_mask(text: str) -> bytearray:
    """Returns a conservative mask for code and raw HTML contexts."""

    mask = bytearray(len(text))
    fence: t.Optional[t.Tuple[str, int, int, int]] = None
    html_end: t.Optional[str] = None
    in_html_block = False
    html_container: t.Optional[t.Tuple[int, int]] = None
    in_indented_code = False
    list_content_indent: t.Optional[int] = None
    previous_blank = True
    offset = 0
    for line in text.splitlines(keepends=True):
        line_end = offset + len(line)
        line_body = line.rstrip("\r\n")
        content_after_quotes = _strip_blockquote_prefix(line_body)
        blank = not content_after_quotes.strip()

        if fence is not None:
            quoted_content = _strip_blockquote_prefix(line_body)
            container_ended = _blockquote_depth(line_body) < fence[3] or (
                fence[2] > 0 and not blank and _leading_indent(quoted_content) < fence[2]
            )
            if container_ended:
                fence = None
            else:
                mask[offset:line_end] = b"\1" * len(line)
                match = _FENCE_RE.match(_strip_indent(quoted_content, fence[2]))
                if (
                    match
                    and match.group(2)[0] == fence[0]
                    and len(match.group(2)) >= fence[1]
                    and not match.group(3).strip()
                ):
                    fence = None
                previous_blank = blank
                offset = line_end
                continue

        if in_html_block:
            assert html_container is not None
            quoted_content = _strip_blockquote_prefix(line_body)
            container_ended = _blockquote_depth(line_body) < html_container[1] or (
                html_container[0] > 0 and not blank and _leading_indent(quoted_content) < html_container[0]
            )
            if container_ended:
                html_end = None
                in_html_block = False
                html_container = None
            else:
                mask[offset:line_end] = b"\1" * len(line)
                if (html_end and html_end in line_body.lower()) or (not html_end and blank):
                    html_end = None
                    in_html_block = False
                    html_container = None
                previous_blank = blank
                offset = line_end
                continue

        match = _FENCE_RE.match(_strip_container_prefix(line_body))
        if match and (match.group(2)[0] != "`" or "`" not in match.group(3)):
            quoted_content = _strip_blockquote_prefix(line_body)
            fence_list_indent = _list_content_indent(quoted_content)
            if (
                fence_list_indent is None
                and list_content_indent is not None
                and _leading_indent(quoted_content) >= list_content_indent
            ):
                fence_list_indent = list_content_indent
            fence = (
                match.group(2)[0],
                len(match.group(2)),
                fence_list_indent or 0,
                _blockquote_depth(line_body),
            )
            mask[offset:line_end] = b"\1" * len(line)
            previous_blank = blank
            offset = line_end
            continue

        container_content = _strip_container_prefix(line_body)
        lowered = container_content.lower()
        if lowered.lstrip().startswith("<!--"):
            in_html_block = "-->" not in lowered
            html_end = "-->" if in_html_block else None
        elif re.match(r"^ {0,3}<!\[CDATA\[", container_content):
            html_end = "]]>"
            in_html_block = html_end not in container_content
        elif re.match(r"^ {0,3}<\?", container_content):
            html_end = "?>"
            in_html_block = html_end not in container_content
        elif re.match(r"^ {0,3}<![A-Z]", container_content):
            html_end = ">"
            in_html_block = html_end not in container_content
        elif re.match(r"^ {0,3}<(?:script|pre|style|textarea)(?:[ \t>]|$)", lowered):
            tag = re.match(r"^ {0,3}<([a-z]+)", lowered)
            assert tag
            html_end = "</{}>".format(tag.group(1))
            in_html_block = html_end not in lowered
        elif _HTML_BLOCK_RE.match(container_content) or (previous_blank and _HTML_TAG_ONLY_RE.match(container_content)):
            in_html_block = True
            html_end = None
        if in_html_block or html_end:
            quoted_content = _strip_blockquote_prefix(line_body)
            html_container = (
                _list_content_indent(quoted_content) or 0,
                _blockquote_depth(line_body),
            )
            mask[offset:line_end] = b"\1" * len(line)
            if html_end and html_end in lowered:
                html_end = None
                in_html_block = False
                html_container = None
            previous_blank = blank
            offset = line_end
            continue

        indent = _leading_indent(content_after_quotes)
        new_list_content_indent = _list_content_indent(content_after_quotes)
        if new_list_content_indent is not None:
            list_content_indent = new_list_content_indent
        elif list_content_indent is not None and not blank and indent < list_content_indent and previous_blank:
            list_content_indent = None
        relative_indent = (
            indent - list_content_indent
            if list_content_indent is not None and indent >= list_content_indent
            else indent
        )
        if in_indented_code:
            if blank or relative_indent >= 4:
                mask[offset:line_end] = b"\1" * len(line)
                previous_blank = blank
                offset = line_end
                continue
            in_indented_code = False
        if relative_indent >= 4 and previous_blank:
            in_indented_code = True
            mask[offset:line_end] = b"\1" * len(line)
            previous_blank = blank
            offset = line_end
            continue

        previous_blank = blank
        offset = line_end

    _mask_html_tags(mask, text, 0, len(text))

    offset = 0
    while offset < len(text):
        if mask[offset] or text[offset] != "`" or _is_escaped(text, offset):
            offset += 1
            continue
        end = offset + 1
        while end < len(text) and text[end] == "`":
            end += 1
        delimiter_length = end - offset
        closing = end
        while closing < len(text):
            if mask[closing] or text[closing] != "`" or _is_escaped(text, closing):
                closing += 1
                continue
            closing_end = closing + 1
            while closing_end < len(text) and text[closing_end] == "`":
                closing_end += 1
            if closing_end - closing == delimiter_length:
                mask[offset:closing_end] = b"\1" * (closing_end - offset)
                offset = closing_end
                break
            closing = closing_end
        else:
            offset = end

    return mask


def _overlaps_mask(mask: bytearray, start: int, end: int) -> bool:
    return any(mask[start:end])


def _overlaps_spans(start: int, end: int, spans: t.Iterable[t.Tuple[int, int]]) -> bool:
    return any(start < span_end and span_start < end for span_start, span_end in spans)


def _find_closing_bracket(text: str, opening: int, nested: bool = False) -> t.Optional[int]:
    depth = 1
    offset = opening + 1
    previous_newline = False
    while offset < len(text):
        char = text[offset]
        if char == "\\":
            offset += 2
            previous_newline = False
            continue
        if char in "\r\n":
            if previous_newline:
                return None
            previous_newline = True
            offset += 2 if char == "\r" and offset + 1 < len(text) and text[offset + 1] == "\n" else 1
            continue
        previous_newline = False
        if nested and char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return offset
        offset += 1
    return None


def _find_closing_parenthesis(text: str, opening: int) -> t.Optional[int]:
    """Finds an inline link's closing parenthesis without treating quotes in its destination as title delimiters."""

    offset = opening + 1
    while offset < len(text) and text[offset].isspace():
        offset += 1

    if offset < len(text) and text[offset] == "<":
        offset += 1
        while offset < len(text) and (text[offset] != ">" or _is_escaped(text, offset)):
            offset += 1
        if offset < len(text):
            offset += 1
    else:
        depth = 0
        while offset < len(text):
            char = text[offset]
            if char == "\\" and offset + 1 < len(text):
                offset += 2
                continue
            if char.isspace() and depth == 0:
                break
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    return offset
                depth -= 1
            offset += 1

    while offset < len(text) and text[offset].isspace():
        offset += 1
    if offset < len(text) and text[offset] == ")":
        return offset

    title_closer = {'"': '"', "'": "'", "(": ")"}.get(text[offset]) if offset < len(text) else None
    if title_closer is not None:
        offset += 1
        while offset < len(text) and (text[offset] != title_closer or _is_escaped(text, offset)):
            offset += 1
        if offset < len(text):
            offset += 1
            while offset < len(text) and text[offset].isspace():
                offset += 1
            if offset < len(text) and text[offset] == ")":
                return offset

    # Preserve the prior behavior for malformed inline links: returning their
    # next balanced delimiter lets the caller inspect nested shortcut links.
    depth = 0
    while offset < len(text):
        if text[offset] == "\\" and offset + 1 < len(text):
            offset += 2
            continue
        if text[offset] == "(":
            depth += 1
        elif text[offset] == ")":
            if depth == 0:
                return offset
            depth -= 1
        offset += 1
    return None


def _is_valid_inline_link(text: str, opening: int, closing: int) -> bool:
    """Validates the destination and optional title inside an inline link."""

    if re.search(r"(?:\r\n|[\r\n])[ \t]*(?:\r\n|[\r\n])", text[opening + 1 : closing]):
        return False

    offset = opening + 1
    while offset < closing and text[offset].isspace():
        offset += 1
    if offset == closing:
        return True

    if text[offset] == "<":
        offset += 1
        destination_start = offset
        while offset < closing and (text[offset] != ">" or _is_escaped(text, offset)):
            if text[offset] in "\r\n<":
                return False
            offset += 1
        if offset == closing or offset == destination_start:
            return False
        offset += 1
    else:
        destination_start = offset
        depth = 0
        while offset < closing and (not text[offset].isspace() or depth):
            if text[offset] == "\\" and offset + 1 < closing and _ESCAPABLE_PUNCTUATION_RE.fullmatch(text[offset + 1]):
                offset += 2
                continue
            if text[offset] in "<>":
                return False
            if text[offset] == "(":
                depth += 1
            elif text[offset] == ")":
                if depth == 0:
                    return False
                depth -= 1
            offset += 1
        if offset == destination_start or depth:
            return False

    while offset < closing and text[offset].isspace():
        offset += 1
    if offset == closing:
        return True

    title_closer = {'"': '"', "'": "'", "(": ")"}.get(text[offset])
    if title_closer is None:
        return False
    offset += 1
    while offset < closing and (text[offset] != title_closer or _is_escaped(text, offset)):
        offset += 1
    if offset == closing:
        return False
    offset += 1
    while offset < closing and text[offset].isspace():
        offset += 1
    return offset == closing


def _image_reference_openings(text: str, start: int, end: int) -> t.List[int]:
    """Returns the bracket offsets of unescaped images in a link's text."""

    result: t.List[int] = []
    offset = start
    while True:
        offset = text.find("![", offset, end)
        if offset < 0:
            return result
        if not _is_escaped(text, offset):
            result.append(offset + 1)
        offset += 2


def _analyze_docstring_references(obj: docspec.ApiObject, content: str) -> _DocstringReferences:
    result = _DocstringReferences(obj, content)
    protected_mask = _markdown_protected_mask(content)
    definition_spans: t.List[t.Tuple[int, int]] = []
    reference_label_spans: t.List[t.Tuple[int, int]] = []
    inline_link_spans: t.List[t.Tuple[int, int]] = []
    inline_image_openings: t.Set[int] = set()

    definition_starts: t.List[t.Tuple[int, int]] = []
    definition_list_indent: t.Optional[int] = None
    previous_blank = True
    line_offset = 0
    for line in content.splitlines(keepends=True):
        line_body = line.rstrip("\r\n")
        content_after_quotes = _strip_blockquote_prefix(line_body)
        blank = not content_after_quotes.strip()
        new_list_content_indent = _list_content_indent(content_after_quotes)
        if new_list_content_indent is not None:
            definition_list_indent = new_list_content_indent
        elif (
            definition_list_indent is not None
            and not blank
            and _leading_indent(content_after_quotes) < definition_list_indent
            and previous_blank
        ):
            definition_list_indent = None
        relative_content = (
            _strip_indent(content_after_quotes, definition_list_indent)
            if definition_list_indent is not None
            and _leading_indent(content_after_quotes) >= definition_list_indent
            and new_list_content_indent is None
            else line_body
        )
        container_content = _strip_container_prefix(relative_content)
        container_offset = len(line_body) - len(container_content)
        match = _REFERENCE_DEFINITION_START_RE.match(container_content)
        if match:
            definition_starts.append((line_offset + container_offset + match.end() - 1, line_offset))
        previous_blank = blank
        line_offset += len(line)

    for opening, line_start in definition_starts:
        closing = _find_closing_bracket(content, opening)
        if closing is None or closing + 1 >= len(content) or content[closing + 1] != ":":
            continue
        if _overlaps_mask(protected_mask, opening, closing + 2) or _is_escaped(content, opening):
            continue
        label_span = (opening + 1, closing)
        label = _normalize_reference_label(content[slice(*label_span)])
        if not label:
            continue
        definition_end = _reference_definition_end(content, closing + 1, label.startswith("^"))
        if definition_end is None:
            continue
        result.definitions.setdefault(label, []).append(label_span)
        definition_spans.append((line_start, definition_end))

    offset = 0
    while offset < len(content):
        opening = content.find("[", offset)
        if opening < 0:
            break
        if protected_mask[opening] or _is_escaped(content, opening):
            offset = opening + 1
            continue
        if _overlaps_spans(opening, opening + 1, reference_label_spans):
            offset = opening + 1
            continue
        if opening not in inline_image_openings and _overlaps_spans(opening, opening + 1, inline_link_spans):
            offset = opening + 1
            continue
        closing = _find_closing_bracket(content, opening, nested=True)
        if closing is None or _overlaps_mask(protected_mask, opening, closing + 1):
            offset = opening + 1
            continue
        if _overlaps_spans(opening, closing + 1, definition_spans):
            offset = closing + 1
            continue

        if closing + 1 < len(content) and content[closing + 1] == "(":
            inline_closing = _find_closing_parenthesis(content, closing + 1)
            if inline_closing is not None and _is_valid_inline_link(content, closing + 1, inline_closing):
                inline_end = inline_closing + 1
                nested_images = _image_reference_openings(content, opening + 1, closing)
                if nested_images:
                    inline_link_spans.append((opening, inline_end))
                    inline_image_openings.update(nested_images)
                    offset = opening + 1
                else:
                    offset = inline_end
                continue

        if closing + 1 < len(content) and content[closing + 1] == "[":
            label_opening = closing + 1
            label_closing = _find_closing_bracket(content, label_opening)
            if label_closing is None or _overlaps_mask(protected_mask, label_opening, label_closing + 1):
                offset = closing + 1
                continue
            label_text = content[label_opening + 1 : label_closing] or content[opening + 1 : closing]
            label_span = (label_opening + 1, label_closing)
            reference_label_spans.append((label_opening, label_closing + 1))
            append = False
            offset = opening + 1 if _image_reference_openings(content, opening + 1, closing) else label_closing + 1
        else:
            label_text = content[opening + 1 : closing]
            if "[" in label_text or "]" in label_text:
                offset = closing + 1
                continue
            label_span = (opening + 1, closing)
            append = not _normalize_reference_label(label_text).startswith("^")
            offset = closing + 1

        label = _normalize_reference_label(label_text)
        if label:
            usage = _ReferenceUsage(closing + 1, closing + 1, append=True) if append else _ReferenceUsage(*label_span)
            result.links.setdefault(label, []).append(usage)

    return result


def _iter_objects(objects: t.Iterable[docspec.ApiObject]) -> t.Iterator[docspec.ApiObject]:
    for obj in objects:
        yield obj
        yield from _iter_objects(getattr(obj, "members", []))


def _reference_slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-.") or "object"


def _rewrite_reference_labels(analysis: _DocstringReferences, labels: t.Dict[str, str]) -> str:
    replacements: t.List[t.Tuple[int, int, str]] = []
    for label, replacement in labels.items():
        replacements.extend((start, end, replacement) for start, end in analysis.definitions[label])
        replacements.extend(
            (usage.start, usage.end, "[{}]".format(replacement) if usage.append else replacement)
            for usage in analysis.links.get(label, [])
        )

    content = analysis.content
    for start, end, replacement in sorted(replacements, reverse=True):
        content = content[:start] + replacement + content[end:]
    return content


def _namespace_duplicate_references(
    objects: t.Iterable[docspec.ApiObject],
    namespace_all: bool = False,
    transform: t.Optional[t.Callable[[str], str]] = None,
) -> t.Dict[int, str]:
    """Rewrites reference labels that would otherwise collide on one rendered page."""

    analyses = []
    for obj in _iter_objects(objects):
        if obj.docstring:
            content = transform(obj.docstring.content) if transform else obj.docstring.content
            analyses.append(_analyze_docstring_references(obj, content))
    owners: t.Dict[str, t.List[_DocstringReferences]] = {}
    used_labels: t.Set[str] = set()
    for analysis in analyses:
        for label in analysis.definitions:
            owners.setdefault(label, []).append(analysis)
        used_labels.update(analysis.definitions)
        used_labels.update(analysis.links)

    rewritten: t.Dict[int, str] = {}
    for analysis in analyses:
        replacements: t.Dict[str, str] = {}
        for label in analysis.definitions:
            if not namespace_all:
                if len(owners[label]) < 2 or label not in analysis.links:
                    continue
            prefix = "^" if label.startswith("^") else ""
            label_slug = label[1:] if prefix else label
            base = prefix + "pydoc-{}-{}".format(
                _reference_slug(dotted_name(analysis.obj)), _reference_slug(label_slug)
            )
            replacement = base
            suffix = 2
            while _normalize_reference_label(replacement) in used_labels:
                replacement = "{}-{}".format(base, suffix)
                suffix += 1
            used_labels.add(_normalize_reference_label(replacement))
            replacements[label] = replacement
        if replacements:
            rewritten[id(analysis.obj)] = _rewrite_reference_labels(analysis, replacements)
    return rewritten


@dataclasses.dataclass
class MarkdownRenderer(Renderer, SinglePageRenderer, SingleObjectRenderer):
    """
    Produces Markdown files. This renderer is often used by other renderers, such as
    #MkdocsRenderer and #HugoRenderer. It provides a wide variety of options to customize
    the generated Markdown files. Reference-style link labels that are duplicated across
    API-object docstrings on the same page are automatically namespaced per object.

    ### Options
    """

    #: The name of the file to render to. If no file is specified, it will
    #: render to stdout.
    filename: t.Optional[str] = None

    #: The encoding of the output file. This is ignored when rendering to
    #: stdout.
    encoding: str = "utf-8"

    #: If enabled, inserts anchors before Markdown headers to ensure that
    #: links to the header work. This is enabled by default.
    insert_header_anchors: bool = True

    #: Generate HTML headers instead of Mearkdown headers. This is disabled
    #: by default.
    html_headers: bool = False

    #: Render names in headers as code (using backticks or `<code>` tags,
    #: depending on #html_headers). This is enabled by default.
    code_headers: bool = False

    #: Generate descriptive class titles by adding the word "Objects" if set to `True`. Otherwise,
    #: it can be a string that is appended or prepended (appended if the string begins with `$`).
    #: the class name. This is enabled by default.
    descriptive_class_title: t.Union[bool, str] = True

    #: Generate descriptivie module titles by adding the word "Module" before
    #: the module name. This is enabled by default.
    descriptive_module_title: bool = False

    #: Add the module name as a prefix to class & method names. This module name is
    #: also rendered as code if #code_headers is enabled. This is enabled
    #: by default.
    add_module_prefix: bool = True

    #: Add the class name as a prefix to method names. This class name is
    #: also rendered as code if #code_headers is enabled. This is enabled
    #: by default.
    add_method_class_prefix: bool = False

    #: Add the class name as a prefix to member names. This is enabled by
    #: default.
    add_member_class_prefix: bool = False

    #: Add the full module name as a prefix to the title of the header.
    #: This is disabled by default.
    add_full_prefix: bool = False

    #: If #add_full_prefix is enabled, this will result in the prefix to
    #: be wrapped in a `<sub>` tag.
    sub_prefix: bool = False

    #: Render the definition of data members as a code block. This is disabled
    #: by default.
    data_code_block: bool = False

    #: Max length of expressions. If this limit is exceeded, the remaining
    #: characters will be replaced with three dots. This is set to 100 by
    #: default.
    data_expression_maxlength: int = 100

    #: Render the class signature as a code block. This includes the "class"
    #: keyword, the class name and its bases. This is enabled by default.
    classdef_code_block: bool = True

    #: Render decorators before class definitions.
    classdef_with_decorators: bool = True

    #: Render classdef and function signature blocks in the Python help()
    #: style.
    signature_python_help_style: bool = False

    #: Render the function signature as a code block. This includes the "def"
    #: keyword, the function name and its arguments. This is enabled by
    #: default.
    signature_code_block: bool = True

    #: Render the function signature in the header. This is disabled by default.
    signature_in_header: bool = False

    #: Render the vertical bar '|' before function signature. This is enabled by default.
    signature_with_vertical_bar: bool = False

    #: Include the "def" keyword in the function signature. This is enabled
    #: by default.
    signature_with_def: bool = True

    #: Render the class name in the code block for function signature. Note
    #: that this results in invalid Python syntax to be rendered. This is
    #: disabled by default.
    signature_class_prefix: bool = False

    #: Render decorators before function definitions.
    signature_with_decorators: bool = True

    #: Render type hints for data elements in the header.
    render_typehint_in_data_header: bool = False

    #: Add the string "python" after the backticks for code blocks. This is
    #: enabled by default.
    code_lang: bool = True

    #: Render title of page at the beginning of the file.
    render_page_title: bool = False

    #: Render a table of contents at the beginning of the file.
    render_toc: bool = False

    #: The title of the "Table of Contents" header.
    render_toc_title: str = "Table of Contents"

    #: The maximum depth of the table of contents. Defaults to 2.
    toc_maxdepth: int = 2

    #: Render module headers. This is enabled by default.
    render_module_header: bool = True

    #: Custom template for module header.
    render_module_header_template: str = ""

    #: Render docstrings as blockquotes. This is disabled by default.
    docstrings_as_blockquote: bool = False

    #: Use a fixed header level for every kind of API object. The individual
    #: levels can be defined with #header_level_by_type.
    use_fixed_header_levels: bool = True

    #: Fixed header levels by API object type.
    header_level_by_type: t.Dict[str, int] = dataclasses.field(
        default_factory=lambda: {
            "Module": 1,
            "Class": 2,
            "Method": 4,
            "Function": 4,
            "Variable": 4,
        }
    )

    #: A plugin that implements the #SourceLinker interface to provide links to the
    #: source code of API objects. If this field is specified, the renderer will
    #: place links to the source code in the generated Markdown files.
    source_linker: t.Optional[SourceLinker] = None

    #: Allows you to define the position of the "view source" link in the Markdown
    #: file if a #source_linker is configured.
    # TODO: Validator.choices(["after signature", "before signature"])
    source_position: str = "after signature"

    #: Allows you to override how the "view source" link is rendered into the Markdown
    #: file if a #source_linker is configured. The default is `[[view_source]]({url})`.
    source_format: str = "[[view_source]]({url})"

    #: Escape html in docstring. Default to False.
    escape_html_in_docstring: bool = False

    #: Render Novella `@anchor` tags before headings.
    render_novella_anchors: bool = False

    #: Format code rendered into Markdown code blocks with YAPF.
    format_code: bool = True

    #: The style to format code as. This can be a YAPF builtin style name or point to
    #: a file relative to the context directory (usually the working directory).
    format_code_style: str = "pep8"

    #: The title of the page when one is not supplied by a parent renderer and
    #: #render_page_title is enabled.
    page_title: t.Optional[str] = None

    def __post_init__(self) -> None:
        self._resolver = MarkdownReferenceResolver()

    def _is_method(self, obj: docspec.ApiObject) -> bool:
        return is_method(obj)

    def _format_arglist(self, func: docspec.Function) -> str:
        args = func.args[:]
        if self._is_method(func) and args and args[0].name == "self":
            args.pop(0)
        return format_arglist(args)

    def _render_toc(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        if level > self.toc_maxdepth:
            return
        object_id = self._resolver.generate_object_id(obj)
        title = self._escape(obj.name)
        if not self.add_module_prefix and isinstance(obj, docspec.Module):
            title = title.split(".")[-1]
        fp.write("  " * level + "* [{}](#{})\n".format(title, object_id))
        level += 1
        for child in getattr(obj, "members", []):
            self._render_toc(fp, level, child)

    def _render_header(self, fp: t.TextIO, level: int, obj: docspec.ApiObject):
        if self.render_module_header_template and isinstance(obj, docspec.Module):
            fp.write(
                self.render_module_header_template.format(
                    module_name=obj.name, relative_module_name=obj.name.rsplit(".", 1)[-1]
                )
            )
            return

        object_id = self._resolver.generate_object_id(obj)
        if self.use_fixed_header_levels:
            # Read the header level based on the API object type. The default levels defined
            # in the field will act as a first fallback, the level of the object inside it's
            # hierarchy is the final fallback.
            header_levels = {
                **type(self).__dataclass_fields__["header_level_by_type"].default_factory(),  # type: ignore
                **self.header_level_by_type,
            }
            # Backwards compat for when we used "Data" instead of "Variable" which mirrors the docspec API
            header_levels["Variable"] = header_levels.get("Data", header_levels["Variable"])

            type_name = "Method" if self._is_method(obj) else type(obj).__name__
            level = header_levels.get(type_name, level)
        if self.insert_header_anchors and not self.html_headers:
            fp.write('<a id="{}"></a>\n\n'.format(object_id))
        if self.html_headers:
            header_template = '<h{0} id="{1}">{{title}}</h{0}>'.format(level, object_id)
        else:
            header_template = level * "#" + " {title}"
        if self.render_novella_anchors:
            fp.write("@anchor pydoc:" + ".".join(x.name for x in obj.path) + "\n")
        fp.write(header_template.format(title=self._get_title(obj)))
        fp.write("\n\n")

    def _format_decorations(self, decorations: t.List[docspec.Decoration]) -> t.Iterable[str]:
        for dec in decorations:
            yield "@{}{}\n".format(dec.name, dec.args or "")

    def _yapf_code(self, code: str) -> str:
        if not self.format_code:
            return code
        style_file = Path(self._context.directory) / self.format_code_style
        style = str(style_file) if style_file.is_file() else self.format_code_style
        return FormatCode(code, style_config=style)[0]

    def _format_function_signature(
        self, func: docspec.Function, override_name: str | None = None, add_method_bar: bool = True
    ) -> str:
        parts: t.List[str] = []
        if self.signature_with_decorators:
            parts += self._format_decorations(func.decorations or [])
        if self.signature_python_help_style and not self._is_method(func):
            parts.append("{} = ".format(dotted_name(func)))
        parts += [x + " " for x in func.modifiers or []]
        if self.signature_with_def:
            parts.append("def ")
        if self.signature_class_prefix and self._is_method(func):
            parent = func.parent
            assert parent, func
            parts.append(parent.name + ".")
        parts.append((override_name or func.name))
        parts.append(format_function_signature(func, self._is_method(func)))
        result = "".join(parts)
        result = self._yapf_code(result + ": pass").rpartition(":")[0].strip()

        if add_method_bar and self._is_method(func):
            result = "\n".join(" | " + line for line in result.split("\n"))
        return result

    def _format_classdef_signature(self, cls: docspec.Class) -> str:
        bases = ", ".join(map(str, cls.bases or []))
        if cls.metaclass:
            if cls.bases:
                bases += ", "
            bases += "metaclass=" + str(cls.metaclass)
        code = "class {}({})".format(cls.name, bases)
        if self.signature_python_help_style:
            code = dotted_name(cls) + " = " + code
        code = self._yapf_code(code + ": pass").rpartition(":")[0].strip()

        if cls.decorations and self.classdef_with_decorators:
            code = "\n".join(self._format_decorations(cls.decorations)) + code
        return code

    def _format_data_signature(self, data: docspec.Variable) -> str:
        expr = str(data.value)
        code = self._yapf_code(data.name + " = " + expr).strip()
        if len(code) > self.data_expression_maxlength:
            code = code[: self.data_expression_maxlength] + " ..."
        return code

    def _render_signature_block(self, fp: t.TextIO, obj: docspec.ApiObject):
        if self.classdef_code_block and isinstance(obj, docspec.Class):
            code = self._format_classdef_signature(obj)
        elif self.signature_code_block and isinstance(obj, docspec.Function):
            code = self._format_function_signature(obj, add_method_bar=self.signature_with_vertical_bar)
        elif self.data_code_block and isinstance(obj, docspec.Variable):
            code = self._format_data_signature(obj)
        else:
            return
        fp.write("```{}\n".format("python" if self.code_lang else ""))
        fp.write(code)
        fp.write("\n```\n\n")

    def _render_object(self, fp: t.TextIO, level: int, obj: docspec.ApiObject, namespaced_docstrings: t.Dict[int, str]):
        if not isinstance(obj, docspec.Module) or self.render_module_header:
            self._render_header(fp, level, obj)

        render_view_source = not isinstance(obj, (docspec.Module, docspec.Variable))

        if render_view_source:
            url = self.source_linker.get_source_url(obj) if self.source_linker else None
            source_string = self.source_format.replace("{url}", str(url)) if url else None
            if source_string and self.source_position == "before signature":
                fp.write(source_string + "\n\n")

        self._render_signature_block(fp, obj)

        if render_view_source:
            if source_string and self.source_position == "after signature":
                fp.write(source_string + "\n\n")

        if obj.docstring:
            if id(obj) in namespaced_docstrings:
                docstring = namespaced_docstrings[id(obj)]
            else:
                content = obj.docstring.content
                docstring = escape_except_blockquotes(content) if self.escape_html_in_docstring else content
            lines = docstring.split("\n")
            if self.docstrings_as_blockquote:
                lines = ["> " + x for x in lines]
            fp.write("\n".join(lines))
            fp.write("\n\n")

    def _render_recursive(
        self, fp: t.TextIO, level: int, obj: docspec.ApiObject, namespaced_docstrings: t.Dict[int, str]
    ):
        self._render_object(fp, level, obj, namespaced_docstrings)
        level += 1
        for member in getattr(obj, "members", []):
            self._render_recursive(fp, level, member, namespaced_docstrings)

    def _get_title(self, obj: docspec.ApiObject) -> str:
        title = obj.name
        if (self.add_method_class_prefix and self._is_method(obj)) or (
            self.add_member_class_prefix and isinstance(obj, docspec.Variable)
        ):
            title = (obj.parent.name + "." + title) if obj.parent else title
        elif self.add_full_prefix and not self._is_method(obj):
            title = dotted_name(obj)
        if not self.add_module_prefix and isinstance(obj, docspec.Module):
            title = title.split(".")[-1]
        if isinstance(obj, docspec.Function):
            if self.signature_in_header:
                title += "(" + self._format_arglist(obj) + ")"

        if isinstance(obj, docspec.Variable) and obj.datatype and self.render_typehint_in_data_header:
            if self.code_headers:
                title += f": {obj.datatype}"
            elif self.html_headers:
                title += f": <code>{obj.datatype}</code>"
            else:
                title += f": `{obj.datatype}`"

        if self.code_headers:
            if self.html_headers or self.sub_prefix:
                if self.sub_prefix and "." in title:
                    prefix, title = title.rpartition(".")[::2]
                    title = "<sub>{}.</sub>{}".format(prefix, title)
                title = "<code>{}</code>".format(title)
            else:
                title = "`{}`".format(title)
        elif not self.html_headers:
            title = self._escape(title)
        if isinstance(obj, docspec.Module) and self.descriptive_module_title:
            title = "Module " + title
        if isinstance(obj, docspec.Class) and self.descriptive_class_title:
            if self.descriptive_class_title is True:
                title += " Objects"
            elif self.descriptive_class_title is False:
                pass
            elif self.descriptive_class_title.startswith("$"):
                title += self.descriptive_class_title[1:]
            else:
                title = self.descriptive_class_title + title
        return title

    def _escape(self, s):
        return s.replace("_", "\\_").replace("*", "\\*")

    def render_to_string(self, modules: t.List[docspec.Module]) -> str:
        fp = io.StringIO()
        self.render_single_page(fp, modules)
        return fp.getvalue()

    def _render_to_stream(self, modules: t.List[docspec.Module], stream: t.TextIO):
        return self.render_single_page(stream, modules)

    # SinglePageRenderer

    def render_single_page(
        self, fp: t.TextIO, modules: t.List[docspec.Module], page_title: t.Optional[str] = None
    ) -> None:
        if page_title is None:
            page_title = self.page_title

        if self.render_page_title:
            if page_title is None:
                raise ValueError(
                    "page_title is required when render_page_title is enabled (set MarkdownRenderer.page_title or pass page_title)."
                )
            fp.write("# {}\n\n".format(page_title))

        if self.render_toc:
            if self.render_toc_title:
                if self.render_page_title:
                    # set to level2 since level1 is page title
                    fp.write("## {}\n\n".format(self.render_toc_title))
                else:
                    fp.write("# {}\n\n".format(self.render_toc_title))

            for m in modules:
                self._render_toc(fp, 0, m)
            fp.write("\n")
        transform = escape_except_blockquotes if self.escape_html_in_docstring else None
        namespaced_docstrings = _namespace_duplicate_references(modules, transform=transform)
        for m in modules:
            self._render_recursive(fp, 1, m, namespaced_docstrings)

    # SingleObjectRenderer

    def render_object(self, fp: t.TextIO, obj: docspec.ApiObject, options: t.Dict[str, t.Any]) -> None:
        # Novella and other integrations may concatenate several independently rendered objects onto one page.
        transform = escape_except_blockquotes if self.escape_html_in_docstring else None
        self._render_recursive(
            fp, 0, obj, _namespace_duplicate_references([obj], namespace_all=True, transform=transform)
        )

    # Renderer

    def get_resolver(self, modules: t.List[docspec.Module]) -> t.Optional[Resolver]:
        """
        Returns a simple #Resolver implementation. Finds cross-references in the same file.
        """

        return self._resolver

    def render(self, modules: t.List[docspec.Module]) -> None:
        if self.filename is None:
            self._render_to_stream(modules, sys.stdout)
        else:
            with io.open(self.filename, "w", encoding=self.encoding) as fp:
                self._render_to_stream(modules, t.cast(t.TextIO, fp))

    # PluginBase

    def init(self, context: Context) -> None:
        if self.source_linker:
            self.source_linker.init(context)
        self._context = context


@dataclasses.dataclass
class MarkdownReferenceResolver(Resolver, ResolverV2):
    local: bool = True
    global_: bool = False

    def generate_object_id(self, obj: docspec.ApiObject) -> str:
        return ".".join(o.name for o in obj.path)

    def _resolve_reference_in_members(
        self, obj: t.Optional[docspec.ApiObject], ref: t.List[str]
    ) -> t.Optional[docspec.ApiObject]:
        if not obj:
            return None
        for part_name in ref:
            obj = docspec.get_member(obj, part_name)
            if not obj:
                return None
        return obj

    def _resolve_local_reference(
        self, scope: docspec.ApiObject, ref_split: t.List[str]
    ) -> t.Optional[docspec.ApiObject]:
        obj: t.Optional[docspec.ApiObject] = scope
        while obj:
            resolved = self._resolve_reference_in_members(obj, ref_split)
            if resolved:
                return resolved
            obj = obj.parent
        return None

    # Resolver

    def resolve_ref(self, scope: docspec.ApiObject, ref: str) -> t.Optional[str]:
        target = self._resolve_local_reference(scope, ref.split("."))
        if target:
            return "#" + self.generate_object_id(target)
        return None

    # ResolverV2

    def resolve_reference(self, suite: ApiSuite, scope: docspec.ApiObject, ref: str) -> t.Optional[docspec.ApiObject]:
        """Resolves the reference by searching in the members of *scope* or any of its parents."""

        # TODO (@NiklasRosenstein): Support resolving indirections

        ref_split = ref.split(".")

        resolved = self._resolve_local_reference(scope, ref_split)
        if resolved:
            return resolved

        if self.global_:

            def _recurse(obj: docspec.ApiObject) -> t.Optional[docspec.ApiObject]:
                resolved = self._resolve_reference_in_members(obj, ref_split)
                if resolved:
                    return resolved
                if isinstance(obj, docspec.HasMembers):
                    for member in obj.members:
                        resolved = _recurse(member)
                        if resolved:
                            return resolved
                return None

            for module in suite:
                resolved = _recurse(module)
                if resolved:
                    return resolved

        return None
