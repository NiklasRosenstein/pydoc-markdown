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
import itertools
import re
import typing as t
import warnings
from contextlib import contextmanager

import docspec
from numpydoc.docscrape import NumpyDocString, Parameter  # type: ignore[import]
from numpydoc.validate import validate  # type: ignore[import]

from pydoc_markdown.interfaces import Processor, Resolver


@contextmanager
def _filter_numpydoc_warnings(action: warnings._ActionKind):
    warnings.filterwarnings(action, module="numpydoc.docscrape")
    yield
    warnings.resetwarnings()


class _DocstringWrapper:
    # Wraps docstrings for use with numpydoc.validate.validate().
    __qualname__ = "pydoc_markdown.contrib.processors.numpy._DocstringWrapper"


@dataclasses.dataclass
class NumpyProcessor(Processor):
    # numpydoc doesn't like when a heading appears twice in the same docstring so we have to use <span> tags to
    # keep numpydoc from recognizing the example headings. This also means the example code block has to be
    # delineated with HTML tags instead of Markdown syntax.
    """
    This processor parses NumPy-style docstrings and converts them to Markdown syntax.

    References
    ----------
    - https://numpydoc.readthedocs.io/en/latest/format.html

    Examples
    --------
    <pre>
    <code>
    <span>Parameters</span>
    ----------
    arg: str
        This argument should be a string.

    <span>Raises</span>
    ------
    ValueError
        If *arg* is not a string.

    <span>Returns</span>
    -------
    int
        The length of the string.
    </code>
    </pre>

    Renders as:

    Parameters
    ----------
    arg : str
        This argument should be a string.

    Raises
    ------
    ValueError
        If *arg* is not a string.

    Returns
    -------
    int
        The length of the string.

    @doc:fmt:numpy
    """

    _SECTION_MAP = {
        "Summary": ["Summary", "Extended Summary"],
        "Arguments": ["Parameters", "Other Parameters"],
        "Returns": ["Returns"],
        "Yields": ["Yields"],
        "Receives": ["Receives"],
        "Attributes": ["Attributes"],
        "Methods": ["Methods"],
        "Raises": ["Raises"],
        "Warns": ["Warns"],
        "Warnings": ["Warnings"],
        "See Also": ["See Also"],
        "Notes": ["Notes"],
        "References": ["References"],
        "Examples": ["Examples"],
    }

    @staticmethod
    def check_docstring_format(docstring: str) -> bool:
        _DocstringWrapper.__doc__ = docstring

        with _filter_numpydoc_warnings("error"):
            try:
                return not validate(_DocstringWrapper.__qualname__).get("Errors")
            except Warning:
                return False

    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        docspec.visit(modules, self._process)

    def _process(self, node: docspec.ApiObject):
        if not node.docstring:
            return

        docstring = NumpyDocString(node.docstring.content)
        lines = []

        # Filter self._SECTION_MAP to only include sections used in the docstring
        active_sections = {k: v for k, v in self._SECTION_MAP.items() if any(docstring.get(sec) for sec in v)}

        # numpydoc is opinionated when it comes to section order so we have to preserve the order of the original
        # docstring ourselves

        # First, we create a regex pattern to match all section headings in the docstring
        keyword_regex = re.compile(
            "|".join(
                [rf"{keyword}(?:\r?\n)-{{{len(keyword)}}}" for keyword in itertools.chain(*active_sections.values())]
            )
        )

        # Second, we strip each patten match of hyphens and whitespace
        keyword_matches = [match.replace("-", "").strip() for match in keyword_regex.findall(node.docstring.content)]

        # Third, we determine the section order in the eventual output based on the order of the headings in the
        # original docstring (but always starting with the summary)
        section_order = [
            "Summary",
            *[next(key for key, value in active_sections.items() if keyword in value) for keyword in keyword_matches],
        ]

        # Finally, we sort active_sections according to the section order we just determined
        for section, keywords in sorted(active_sections.items(), key=lambda x: section_order.index(x[0])):
            lines.extend(self._get_section_contents(docstring, section, keywords))

        node.docstring.content = "\n".join(lines)

    def _get_section_contents(self, docstring: NumpyDocString, section: str, keywords: list) -> list[str]:
        contents = list(itertools.chain([docstring.get(sec) for sec in keywords]))

        if section == "Summary":
            return self._parse_summary(contents)
        else:
            # contents needs to be flattened for all sections aside from Summary
            contents = list(itertools.chain(*contents))
            if section in ["Notes", "References"]:
                return self._parse_notes_and_references(section, contents)
            elif section == "Examples":
                return self._parse_examples(contents)
            elif section == "See Also":
                return self._parse_see_also(contents)
            elif any(isinstance(item, Parameter) for item in contents):
                return self._parse_parameters(section, contents)
            else:
                return [f"\n**{section}**\n", *contents] if contents else []

    @staticmethod
    def _parse_summary(contents: list[str]) -> list[str]:
        summary, extended = contents
        return [*summary, "", *extended] if extended else [*summary]

    @staticmethod
    def _parse_parameters(section: str, parameters: list[Parameter]) -> list[str]:
        lines = []

        for param in parameters:
            name, cls, desc = param
            desc = "\n".join(desc)

            if name and cls and desc:
                lines.append(f"* **{name}** (`{cls}`): {desc}")
            elif name and cls:
                lines.append(f"* **{name}** (`{cls}`)")
            elif name and desc:
                lines.append(f"* **{name}**: {desc}")
            elif cls and desc:
                lines.append(f"* `{cls}`: {desc}")
            elif name:
                lines.append(f"* **{name}**")
            elif cls:
                lines.append(f"* `{cls}`")
            elif desc:
                lines.append(f"* {desc}")

        return [f"\n**{section}**\n", *lines] if lines else []

    @staticmethod
    def _parse_notes_and_references(section: str, contents: list[str]) -> list[str]:
        content_string = "\n".join(contents)
        citations = re.compile("(\.\. )?\[(?P<ref_id>\w+)][_ ]?")

        replacements = {"Notes": "<sup>{ref_id}</sup>", "References": "{ref_id}. "}

        for match in citations.finditer(content_string):
            ref_id = match.group("ref_id")
            content_string = content_string.replace(match.group(0), replacements[section].format(ref_id=ref_id))

        return [f"\n**{section}**\n", *content_string.splitlines()]

    @staticmethod
    def _parse_examples(contents: list[str]) -> list[str]:
        # Wraps doctests in Python codeblocks and leaves all other content as is
        doctests = re.compile(r"(>>>(?:.+(?:\r?\n|$))+)", flags=re.MULTILINE)
        return [
            "\n**Examples**\n",
            *doctests.sub("```python\n\g<0>\n```", "\n".join(contents)).splitlines(),
        ]

    @staticmethod
    def _parse_see_also(contents: list[tuple]) -> list[str]:
        lines = []

        for group in contents:
            sublines = []
            objs, desc = group

            sublines.append("* " + ", ".join([f":{obj[1]}:`{obj[0]}`" if obj[1] else f"{obj[0]}" for obj in objs]))

            if desc:
                sublines[-1] += ": " + "\n".join(desc)

            lines.extend(sublines)

        return [f"\n**See Also**\n", *lines]
