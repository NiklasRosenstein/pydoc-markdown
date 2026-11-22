"""
Namespacing of Markdown reference-style link labels across docstrings rendered onto the same page.

Markdown resolves `[text][label]` against the first `[label]: url` definition on the page. When two docstrings on one
page both define `[label]`, the second docstring's links silently point to the first docstring's target. These helpers
rename such labels per docstring.
"""

import re
import typing as t

import docspec

_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CODE_SPAN_RE = re.compile(r"(`+)[\s\S]*?(?<!`)\1(?!`)")
# Footnote labels (`[^1]`) are left alone, since renaming them would break the footnote syntax.
_DEFINITION_RE = re.compile(r"^( {0,3}\[)((?!\^)[^\[\]\n]+)(\]:[ \t]*\S.*)$")
# `[text][label]`, `[label][]` or `[label]`, but not an inline link `[text](url)` or a definition `[label]:`.
_REFERENCE_RE = re.compile(r"(?<!\\)\[([^\[\]\n]+)\](?:\[([^\[\]\n]*)\])?(?![(:\[])")


def _normalize(label: str) -> str:
    return " ".join(label.split()).casefold()


def _iter_markdown_lines(content: str) -> t.Iterator[t.Tuple[str, bool]]:
    """Yields every line of *content* together with whether it is outside of a fenced code block."""

    fence: t.Optional[str] = None
    for line in content.split("\n"):
        match = _FENCE_RE.match(line)
        if fence is None and match:
            fence = match.group(1)
            yield line, False
        elif fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            yield line, False
        else:
            yield line, True


def _sub_outside_code_spans(line: str, function: t.Callable[["re.Match[str]"], str]) -> str:
    parts = []
    position = 0
    for match in _CODE_SPAN_RE.finditer(line):
        parts.append(_REFERENCE_RE.sub(function, line[position : match.start()]))
        parts.append(match.group())
        position = match.end()
    parts.append(_REFERENCE_RE.sub(function, line[position:]))
    return "".join(parts)


def _analyze(content: str) -> t.Tuple[t.Set[str], t.Set[str]]:
    """Returns the normalized labels that *content* defines and the ones it references."""

    defined: t.Set[str] = set()
    used: t.Set[str] = set()

    def collect(match: "re.Match[str]") -> str:
        used.add(_normalize(match.group(2) or match.group(1)))
        return match.group()

    for line, is_markdown in _iter_markdown_lines(content):
        if not is_markdown:
            continue
        definition = _DEFINITION_RE.match(line)
        if definition:
            defined.add(_normalize(definition.group(2)))
        else:
            _sub_outside_code_spans(line, collect)
    return defined, used


def _rename(content: str, labels: t.Dict[str, str]) -> str:
    def replace(match: "re.Match[str]") -> str:
        label = labels.get(_normalize(match.group(2) or match.group(1)))
        return match.group() if label is None else "[{}][{}]".format(match.group(1), label)

    lines = []
    for line, is_markdown in _iter_markdown_lines(content):
        if is_markdown:
            definition = _DEFINITION_RE.match(line)
            if definition:
                label = labels.get(_normalize(definition.group(2)))
                if label is not None:
                    line = definition.group(1) + label + definition.group(3)
            else:
                line = _sub_outside_code_spans(line, replace)
        lines.append(line)
    return "\n".join(lines)


def _iter_objects(objects: t.Iterable[docspec.ApiObject]) -> t.Iterator[docspec.ApiObject]:
    for obj in objects:
        yield obj
        yield from _iter_objects(getattr(obj, "members", []))


def namespace_reference_links(
    objects: t.Iterable[docspec.ApiObject],
    namespaced_name: t.Callable[[docspec.ApiObject], str],
    rename_unique: bool = False,
) -> t.Dict[int, str]:
    """
    Renames reference labels in the docstrings of *objects* and their members, which are rendered onto one page.
    Renamed labels are prefixed with `namespaced_name(obj)`.

    A label is renamed in a docstring only if that docstring both defines and references it, and no docstring on the
    page references it without defining it (that docstring relies on a definition elsewhere on the page).
    Unless *rename_unique* is set, a label is also only renamed if more than one docstring defines it. Set
    *rename_unique* when the rest of the page is not known, e.g. when objects are rendered individually.

    Returns the rewritten docstrings, keyed by the `id()` of their API object. Docstrings without changes are omitted.
    """

    analyses = [
        (obj, obj.docstring.content, *_analyze(obj.docstring.content))
        for obj in _iter_objects(objects)
        if obj.docstring
    ]
    definition_counts: t.Dict[str, int] = {}
    relies_on_page: t.Set[str] = set()
    for _obj, _content, defined, used in analyses:
        for label in defined:
            definition_counts[label] = definition_counts.get(label, 0) + 1
        relies_on_page |= used - defined

    result: t.Dict[int, str] = {}
    for obj, content, defined, used in analyses:
        labels = {
            label: "{}--{}".format(namespaced_name(obj), label)
            for label in defined & used
            if label not in relies_on_page and (rename_unique or definition_counts[label] > 1)
        }
        if labels:
            result[id(obj)] = _rename(content, labels)
    return result
