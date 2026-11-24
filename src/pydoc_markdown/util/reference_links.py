"""
Namespacing of Markdown reference-style link labels across docstrings rendered onto the same page.

Markdown resolves `[text][label]` against the first `[label]: url` definition on the page. When two docstrings on one
page both define `[label]`, the second docstring's links silently point to the first docstring's target. These helpers
rename such labels per docstring.

The helpers recognise the common forms of reference links line by line rather than parsing Markdown fully. A label is
only renamed when both its definition and its uses are recognised, so anything unusual is left as it is.
"""

import re
import typing as t

import docspec

_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CODE_SPAN_RE = re.compile(r"(`+)[\s\S]*?(?<!`)\1(?!`)")
# Footnote labels (`[^1]`) are left alone, since renaming them would break the footnote syntax.
_DEFINITION_RE = re.compile(r"^( {0,3}\[)((?!\^)[^\[\]\n]+)(\]:[ \t]*\S.*)$")
_REFERENCE_RE = re.compile(
    # The label of a full reference `[text][label]`. Matching from the closing bracket of the text supports any link
    # text, including text wrapped over several lines, inline code and images.
    r"\]\[(?P<full>[^\[\]\n]+)\]"
    # A collapsed reference `[label][]`.
    r"|(?<![\]\\])\[(?P<collapsed>[^\[\]\n]+)\]\[\]"
    # A shortcut reference `[label]`, which is not the text of a full reference or an inline link `[text](url)`.
    r"|(?<![\]\\])\[(?P<shortcut>[^\[\]\n]+)\](?![\[(])"
)


def _normalize(label: str) -> str:
    return " ".join(label.split()).casefold()


def _indentation(line: str) -> int:
    return len(line.expandtabs(4)) - len(line.expandtabs(4).lstrip())


def _iter_markdown_lines(content: str) -> t.Iterator[t.Tuple[str, bool]]:
    """Yields every line of *content* together with whether it is outside of a fenced code block."""

    fence: t.Optional[str] = None
    for line in content.split("\n"):
        match = _FENCE_OPEN_RE.match(line)
        if fence is None and match:
            fence = match.group(1)
            yield line, False
        elif fence is not None:
            closer = match.group(1) if match else ""
            if closer[:1] == fence[0] and len(closer) >= len(fence) and not line.strip()[len(closer) :].strip():
                fence = None
            yield line, False
        else:
            yield line, True


def _sub_references(line: str, function: t.Callable[["re.Match[str]"], str]) -> str:
    """Applies *function* to every reference in *line* that is not inside inline code."""

    parts = []
    position = 0
    for match in _CODE_SPAN_RE.finditer(line):
        parts.append(_REFERENCE_RE.sub(function, line[position : match.start()]))
        parts.append(match.group())
        position = match.end()
    parts.append(_REFERENCE_RE.sub(function, line[position:]))
    return "".join(parts)


def _label(match: "re.Match[str]") -> str:
    return _normalize(match.group("full") or match.group("collapsed") or match.group("shortcut"))


def _analyze(content: str) -> t.Tuple[t.Set[str], t.Set[str], t.Set[str]]:
    """
    Returns the normalized labels that *content* defines, the ones it references, and the ones that must not be
    renamed because they also appear on a line indented by four or more spaces. Such a line may be part of an indented
    code block, e.g. a doctest that subscripts with `x[1]`.
    """

    defined: t.Set[str] = set()
    used: t.Set[str] = set()
    unsafe: t.Set[str] = set()

    for line, is_markdown in _iter_markdown_lines(content):
        if not is_markdown:
            continue
        definition = _DEFINITION_RE.match(line)
        if definition:
            defined.add(_normalize(definition.group(2)))
            continue
        labels: t.Set[str] = set()

        def collect(match: "re.Match[str]") -> str:
            labels.add(_label(match))
            return match.group()

        _sub_references(line, collect)
        used |= labels
        if _indentation(line) >= 4:
            unsafe |= labels
    return defined, used, unsafe


def _rename(content: str, labels: t.Dict[str, str]) -> str:
    def replace(match: "re.Match[str]") -> str:
        label = labels.get(_label(match))
        if label is None:
            return match.group()
        if match.group("full"):
            return "][{}]".format(label)
        text = match.group("collapsed") or match.group("shortcut")
        return "[{}][{}]".format(text, label)

    lines = []
    for line, is_markdown in _iter_markdown_lines(content):
        if is_markdown:
            definition = _DEFINITION_RE.match(line)
            if definition:
                label = labels.get(_normalize(definition.group(2)))
                if label is not None:
                    line = definition.group(1) + label + definition.group(3)
            else:
                line = _sub_references(line, replace)
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
    page references it without defining it (that docstring relies on a definition elsewhere on the page). Unless
    *rename_unique* is set, a label is also only renamed if more than one docstring defines it. Set *rename_unique*
    when the rest of the page is not known, e.g. when objects are rendered individually.

    Returns the rewritten docstrings, keyed by the `id()` of their API object. Docstrings without changes are omitted.
    """

    analyses = [
        (obj, obj.docstring.content, *_analyze(obj.docstring.content))
        for obj in _iter_objects(objects)
        if obj.docstring
    ]
    definition_counts: t.Dict[str, int] = {}
    relies_on_page: t.Set[str] = set()
    taken: t.Set[str] = set()
    for _obj, _content, defined, used, _unsafe in analyses:
        for label in defined:
            definition_counts[label] = definition_counts.get(label, 0) + 1
        relies_on_page |= used - defined
        taken |= defined | used

    result: t.Dict[int, str] = {}
    for obj, content, defined, used, unsafe in analyses:
        labels: t.Dict[str, str] = {}
        for label in sorted((defined & used) - unsafe - relies_on_page):
            if not rename_unique and definition_counts[label] < 2:
                continue
            # Objects can share a name (e.g. a redefined function), so make sure that the new label is unique.
            base = _normalize("{}--{}".format(namespaced_name(obj), label))
            new_label, suffix = base, 2
            while new_label in taken:
                new_label, suffix = "{}-{}".format(base, suffix), suffix + 1
            taken.add(new_label)
            labels[label] = new_label
        if labels:
            result[id(obj)] = _rename(content, labels)
    return result
