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

import dataclasses
import inspect
import logging
import re
import typing as t

import docspec
import docstring_parser

from pydoc_markdown.interfaces import Processor, Resolver

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class _ParamLine:
    """
    Helper data class for holding details of Sphinx arguments.
    """

    name: str
    docs: str
    type: t.Optional[str] = None


def generate_sections_markdown(lines, sections):
    for key, section in sections.items():
        if section:
            if lines and lines[-1]:
                lines.append("")
            lines.extend(["**{}**:".format(key), ""])
            lines.extend(section)


def _markdown_list_item(value: str) -> str:
    """Format multiline content as a Markdown list item."""

    return "- " + value.replace("\n", "\n  ")


_MARKDOWN_FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_MARKDOWN_CONTAINER_RE = re.compile(r"^(?:[ \t]*(?:[-+*]|\d{1,9}[.)])|[ \t]*(?:!!!|\?\?\?))[ \t]+")
_MARKDOWN_SECTION_RE = re.compile(r"^[ \t]*\S.*:[ \t]*$")


def _leading_width(line: str) -> int:
    whitespace = line[: len(line) - len(line.lstrip())]
    return len(whitespace.expandtabs(4))


def _split_blockquote_prefix(line: str, container_indent: int = 0) -> t.Tuple[str, str]:
    offset = 0
    column = 0
    while offset < len(line) and column < container_indent and line[offset] in " \t":
        if line[offset] == " ":
            column += 1
        else:
            column += 4 - column % 4
        offset += 1
    if column < container_indent:
        offset = 0
    found_quote = False
    while True:
        marker = offset
        spaces = 0
        while marker < len(line) and line[marker] == " " and spaces < 3:
            marker += 1
            spaces += 1
        if line.startswith(">>>", marker):
            return (line[:offset], line[offset:]) if found_quote else ("", line)
        if marker >= len(line) or line[marker] != ">":
            return (line[:offset], line[offset:]) if found_quote else ("", line)
        found_quote = True
        offset = marker + 1
        if offset < len(line) and line[offset] in " \t":
            offset += 1


def _active_container_indent(lines: t.Iterable[str], quote_prefix: str, current_indent: int) -> int:
    """Returns the content indentation of the active list or admonition container."""

    minimum_child_indent = current_indent
    for previous in reversed(list(lines)):
        if not previous.strip():
            continue
        previous_quote_prefix, previous_content = _split_blockquote_prefix(previous)
        if previous_quote_prefix != quote_prefix:
            break
        match = _MARKDOWN_CONTAINER_RE.match(previous_content)
        if match:
            content_indent = len(match.group().expandtabs(4))
            if content_indent <= current_indent and minimum_child_indent >= content_indent:
                return content_indent
        elif _MARKDOWN_SECTION_RE.match(previous_content):
            content_indent = _leading_width(previous_content) + 4
            if content_indent <= current_indent and minimum_child_indent >= content_indent:
                return content_indent
        minimum_child_indent = min(minimum_child_indent, _leading_width(previous_content))
    return 0


def get_markdown_fence_opener(line: str, container_indent: int = 0) -> t.Optional[t.Tuple[str, int, int]]:
    """Return the character and length of a Markdown fence opener, if any."""

    opener_indent = _leading_width(line)
    if opener_indent > container_indent + 3:
        return None
    match = _MARKDOWN_FENCE_RE.match(line.lstrip())
    if not match:
        return None
    fence = match.group("fence")
    if fence[0] == "`" and "`" in match.group("info"):
        return None
    return fence[0], len(fence), container_indent


def is_markdown_fence_closer(line: str, fence: t.Tuple[str, int, int]) -> bool:
    """Return whether *line* closes the Markdown fence described by *fence*."""

    character, minimum_length, container_indent = fence
    if _leading_width(line) > container_indent + 3:
        return False
    stripped = line.strip()
    return len(stripped) >= minimum_length and all(value == character for value in stripped)


def fence_doctest_blocks(text: str, replacement: t.Optional[t.Callable[[str], str]] = None) -> str:
    """Wrap doctest blocks in a Python Markdown fence.

    A block starts with a ``>>>`` prompt and ends at the next blank line. Existing Markdown fences
    are preserved, and generated fences are long enough not to collide with the block's contents.
    """

    lines: t.List[str] = []
    doctest_lines: t.List[str] = []
    doctest_indent = 0
    doctest_prefix = ""
    doctest_source_prefix = ""
    doctest_quote_prefix = ""
    markdown_fence: t.Optional[t.Tuple[str, int, int]] = None
    markdown_fence_quote_depth = 0
    markdown_fence_container_indent = 0

    def flush_doctest() -> None:
        if not doctest_lines:
            return
        longest_run = max(
            (len(match.group()) for line in doctest_lines for match in re.finditer(r"`+", line)), default=0
        )
        fence = "`" * max(3, longest_run + 1)
        rendered = "\n".join(
            [
                doctest_prefix + fence + "python",
                *(doctest_prefix + line for line in doctest_lines),
                doctest_prefix + fence,
            ]
        )
        if replacement:
            lines.append(doctest_source_prefix + replacement(rendered))
        else:
            lines.extend(rendered.split("\n"))
        doctest_lines.clear()

    for line in text.split("\n"):
        structural_indent = _active_container_indent(lines, "", _leading_width(line))
        quote_prefix, unquoted_line = _split_blockquote_prefix(line, structural_indent)
        stripped = unquoted_line.lstrip()

        if doctest_lines:
            if quote_prefix != doctest_quote_prefix:
                flush_doctest()
            elif not stripped:
                flush_doctest()
                lines.append(line)
                continue
            leading_length = len(unquoted_line) - len(stripped)
            if quote_prefix == doctest_quote_prefix and leading_length >= doctest_indent:
                doctest_lines.append(unquoted_line[min(doctest_indent, leading_length) :])
                continue
            if doctest_lines:
                flush_doctest()

        if markdown_fence is not None:
            quote_depth = quote_prefix.count(">")
            container_ended = (markdown_fence_quote_depth and quote_depth < markdown_fence_quote_depth) or (
                markdown_fence_container_indent
                and stripped
                and _leading_width(unquoted_line) < markdown_fence_container_indent
            )
            if container_ended:
                markdown_fence = None
            else:
                lines.append(line)
                if quote_depth == markdown_fence_quote_depth and is_markdown_fence_closer(
                    unquoted_line, markdown_fence
                ):
                    markdown_fence = None
                continue

        container_indent = _active_container_indent(lines, quote_prefix, _leading_width(unquoted_line))
        markdown_fence = get_markdown_fence_opener(unquoted_line, container_indent)
        if markdown_fence is not None:
            markdown_fence_quote_depth = quote_prefix.count(">")
            markdown_fence_container_indent = container_indent
            lines.append(line)
            continue

        if re.match(r"^>>>($|\s)", stripped):
            doctest_indent = len(unquoted_line) - len(stripped)
            doctest_quote_prefix = quote_prefix
            doctest_source_prefix = quote_prefix + unquoted_line[:doctest_indent]
            doctest_prefix = quote_prefix
            for previous in reversed(lines):
                if not previous.strip():
                    continue
                _, previous_content = _split_blockquote_prefix(previous)
                if _leading_width(previous_content) >= doctest_indent:
                    continue
                if re.match(r"^\s*(?:[-+*]|\d{1,9}[.)])(?:[ \t]+|$)", previous_content) or re.match(
                    r"^\s*(?:!!!|\?\?\?)(?:[ \t]+|$)", previous_content
                ):
                    doctest_prefix += unquoted_line[:doctest_indent]
                break
            doctest_lines.append(stripped)
        else:
            lines.append(line)

    flush_doctest()

    return "\n".join(lines)


def _protect_doctest_blocks(text: str) -> t.Tuple[str, t.Dict[str, str]]:
    replacements: t.Dict[str, str] = {}

    def replace(block: str) -> str:
        index = len(replacements)
        token = "__PYDOC_MARKDOWN_DOCTEST_BLOCK_{}__".format(index)
        while token in text or token in replacements or any(token in value for value in replacements.values()):
            index += 1
            token = "__PYDOC_MARKDOWN_DOCTEST_BLOCK_{}__".format(index)
        replacements[token] = block
        return token

    return fence_doctest_blocks(text, replace), replacements


def _restore_doctest_blocks(content: str, replacements: t.Dict[str, str]) -> str:
    """Restore protected doctests, keeping embedded field descriptions valid Markdown."""

    def preceding_container_indent(offset: int) -> int:
        minimum_child_indent: t.Optional[int] = None
        previous_content = content[:offset].rstrip("\r\n")
        for previous_line in reversed(previous_content.splitlines()):
            if not previous_line.strip():
                continue
            marker = _MARKDOWN_CONTAINER_RE.match(previous_line)
            if marker:
                container_indent = len(marker.group().expandtabs(4))
                if minimum_child_indent is None or minimum_child_indent >= container_indent:
                    return container_indent
            line_indent = _leading_width(previous_line)
            if line_indent == 0:
                return 0
            minimum_child_indent = (
                line_indent if minimum_child_indent is None else min(minimum_child_indent, line_indent)
            )
        return 0

    for token, block in replacements.items():
        standalone_pattern = r"(?m)^[ \t]*(?:>[ \t]?)*[ \t]*{}[ \t]*$".format(re.escape(token))

        def restore_standalone(match: t.Match[str]) -> str:
            container_indent = preceding_container_indent(match.start())
            if not container_indent:
                return block
            indent = " " * container_indent
            indented_block = "\n".join(indent + line for line in block.splitlines())
            return "\n" + indented_block

        content, count = re.subn(standalone_pattern, restore_standalone, content)
        if count:
            continue

        embedded_pattern = r"(?m)^(?P<prefix>[^\r\n]*\S)[ \t]*{}[ \t]*$".format(re.escape(token))

        def restore_embedded(match: t.Match[str]) -> str:
            prefix = match.group("prefix").rstrip()
            marker = _MARKDOWN_CONTAINER_RE.match(prefix)
            indent = " " * (len(marker.group().expandtabs(4)) if marker else _leading_width(prefix))
            indented_block = "\n".join(indent + line for line in block.splitlines())
            return prefix + "\n\n" + indented_block

        content, count = re.subn(embedded_pattern, restore_embedded, content)
        if not count:
            content = content.replace(token, block)
    return content


@dataclasses.dataclass
class SphinxProcessor(Processor):
    """
    This processor parses ReST/Sphinx, Google, NumPy and Epydoc-style function documentation
    and converts it into Markdown syntax. Set #style to select a specific format, or leave it
    as #docstring_parser.DocstringStyle.AUTO to detect the format automatically.

    Example:

    ```
    :param arg1: This is the first argument.
    :raise ValueError: If *arg1* is a bad value.
    :return: An `int` that represents an interesting value.
    ```

    Renders as:

    :param arg1: This is the first argument.
    :raise ValueError: If *arg1* is a bad value.
    :return: An `int` that represents an interesting value.

    @doc:fmt:sphinx
    """

    style: docstring_parser.DocstringStyle = docstring_parser.DocstringStyle.AUTO

    #: Wrap doctest prompt blocks in collision-safe Python Markdown fences.
    render_doctest_blocks: bool = True

    _KEYWORDS = {
        "Arguments": [
            "arg",
            "argument",
            "param",
            "parameter",
            "type",
        ],
        "Returns": [
            "return",
            "returns",
            "rtype",
        ],
        "Raises": [
            "raises",
            "raise",
        ],
    }

    def check_docstring_format(self, docstring: str) -> bool:
        if self.style in (docstring_parser.DocstringStyle.AUTO, docstring_parser.DocstringStyle.REST):
            if any(f":{k}" in docstring for _, value in self._KEYWORDS.items() for k in value):
                return True

        if self.style not in (docstring_parser.DocstringStyle.AUTO, docstring_parser.DocstringStyle.NUMPYDOC):
            return False

        try:
            parsed = docstring_parser.parse(docstring, docstring_parser.DocstringStyle.AUTO)
        except docstring_parser.ParseError:
            return False
        return parsed.style == docstring_parser.DocstringStyle.NUMPYDOC

    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        docspec.visit(modules, self._process)

    def _convert_raises(self, raises: t.List[docstring_parser.common.DocstringRaises]) -> list:
        """Convert a list of DocstringRaises from docstring_parser to markdown lines

        :return: A list of markdown formatted lines
        """
        converted_lines = []
        for entry in raises:
            converted_lines.append(_markdown_list_item("`{}`: {}".format(entry.type_name, entry.description or "")))
        return converted_lines

    def _convert_params(self, params: t.List[docstring_parser.common.DocstringParam]) -> list:
        """Convert a list of DocstringParam to markdown lines.

        :return: A list of markdown formatted lines
        """
        converted = []
        for param in params:
            qualifiers = []
            if param.type_name:
                qualifiers.append("`{}`".format(param.type_name))
            if param.is_optional:
                qualifiers.append("optional")
            if param.default is not None:
                qualifiers.append("default: `{}`".format(param.default))
            details = " ({})".format(", ".join(qualifiers)) if qualifiers else ""
            converted.append(
                _markdown_list_item(
                    "`{name}`{details}: {description}".format(
                        name=param.arg_name, details=details, description=param.description or ""
                    )
                )
            )
        return converted

    def _convert_returns(self, returns: t.List[docstring_parser.common.DocstringReturns]) -> t.List[str]:
        """Convert DocstringReturns objects to Markdown lines.

        :return: Markdown-formatted lines
        """
        converted = []
        for entry in returns:
            if entry.return_name and entry.type_name:
                prefix = "`{}` (`{}`): ".format(entry.return_name, entry.type_name)
            elif entry.return_name:
                prefix = "`{}`: ".format(entry.return_name)
            elif entry.type_name:
                prefix = "`{}`: ".format(entry.type_name)
            else:
                prefix = ""
            converted.append(prefix + (entry.description or ""))

        if len(converted) > 1:
            return [_markdown_list_item(entry) for entry in converted]
        return converted

    @staticmethod
    def _convert_metadata(
        parsed_docstring: docstring_parser.Docstring, handled: t.Iterable[docstring_parser.common.DocstringMeta]
    ) -> t.Dict[str, t.List[str]]:
        """Preserve parsed sections that do not have a dedicated converter."""

        handled_ids = {id(entry) for entry in handled}
        converted: t.Dict[str, t.List[str]] = {}
        for entry in parsed_docstring.meta:
            if id(entry) in handled_ids or not entry.args:
                continue
            heading_key = entry.args[0].replace("_", " ").casefold()
            heading = {
                "attribute": "Attributes",
                "example": "Examples",
                "method": "Methods",
                "note": "Notes",
                "reference": "References",
                "warning": "Warnings",
            }.get(heading_key, heading_key.title())
            description = entry.description or ""
            snippet = getattr(entry, "snippet", None)
            if heading_key in ("example", "examples") and snippet:
                description = "{}\n{}".format(snippet, description) if description else snippet
            identifier = " ".join(entry.args[1:])
            if identifier:
                description = "`{}`: {}".format(identifier, description)
            converted.setdefault(heading, []).append(description)
        for heading, entries in converted.items():
            if len(entries) > 1:
                converted[heading] = [_markdown_list_item(entry) for entry in entries]
        return converted

    def _process(self, node: docspec.ApiObject) -> None:
        if not node.docstring:
            return

        lines = []
        components: t.Dict[str, t.List[str]] = {}

        content = node.docstring.content
        protected_doctests: t.Dict[str, str] = {}
        if self.render_doctest_blocks:
            content, protected_doctests = _protect_doctest_blocks(content)
        parsed_docstring = docstring_parser.parse(content, self.style)
        self._restore_rest_description_indentation(content, parsed_docstring)
        attribute_params = [
            entry
            for entry in parsed_docstring.params
            if entry.args and entry.args[0].casefold() in ("attribute", "cvar", "ivar", "var")
        ]
        other_params = [
            entry for entry in parsed_docstring.params if entry.args and entry.args[0].casefold() == "other_param"
        ]
        argument_params = [
            entry for entry in parsed_docstring.params if entry not in attribute_params and entry not in other_params
        ]
        components["Arguments"] = self._convert_params(argument_params)
        components["Attributes"] = self._convert_params(attribute_params)
        components["Other Parameters"] = self._convert_params(other_params)
        warnings = [
            entry
            for entry in parsed_docstring.raises
            if getattr(entry, "is_warning", False)
            or (entry.args and entry.args[0].replace("_", " ").casefold() in ("warn", "warns", "warning", "warnings"))
        ]
        raises = [entry for entry in parsed_docstring.raises if entry not in warnings]
        components["Raises"] = self._convert_raises(raises)
        components["Warnings"] = self._convert_raises(warnings)
        returns = [entry for entry in parsed_docstring.many_returns if not entry.is_generator]
        yields = [entry for entry in parsed_docstring.many_returns if entry.is_generator]
        components["Returns"] = self._convert_returns(returns)
        components["Yields"] = self._convert_returns(yields)
        handled = [*parsed_docstring.params, *parsed_docstring.raises, *parsed_docstring.many_returns]
        for heading, entries in self._convert_metadata(parsed_docstring, handled).items():
            if components.get(heading) and entries:
                combined = [*components[heading], *entries]
                components[heading] = [
                    entry if entry.startswith("- ") else _markdown_list_item(entry) for entry in combined
                ]
            else:
                components[heading] = entries

        if parsed_docstring.short_description:
            lines.append(parsed_docstring.short_description)
            lines.append("")
        if parsed_docstring.long_description:
            lines.append(parsed_docstring.long_description)
            lines.append("")

        generate_sections_markdown(lines, components)
        node.docstring.content = _restore_doctest_blocks("\n".join(lines), protected_doctests)

    @staticmethod
    def _restore_rest_description_indentation(text: str, parsed_docstring: docstring_parser.Docstring) -> None:
        """Restore indentation stripped from the first line of a ReST long description.

        ``docstring_parser`` strips all leading whitespace from the long-description chunk. This
        loses the first line's indentation when an indented Markdown code block immediately follows
        the short description. Only restore the prefix when the parsed line otherwise matches the
        source, leaving the parser's normalization unchanged for ordinary prose.
        """

        if parsed_docstring.style != docstring_parser.DocstringStyle.REST or not parsed_docstring.long_description:
            return

        cleaned = inspect.cleandoc(text)
        metadata = re.search("^:", cleaned, flags=re.MULTILINE)
        description = cleaned[: metadata.start()] if metadata else cleaned
        parts = description.split("\n", 1)
        if len(parts) == 1:
            return

        source_long_description = parts[1].lstrip("\r\n")
        if not source_long_description:
            return

        source_first_line = source_long_description.splitlines()[0]
        parsed_first_line = parsed_docstring.long_description.splitlines()[0]
        indentation = source_first_line[: len(source_first_line) - len(source_first_line.lstrip())]
        if indentation and source_first_line.lstrip() == parsed_first_line:
            parsed_docstring.long_description = indentation + parsed_docstring.long_description
