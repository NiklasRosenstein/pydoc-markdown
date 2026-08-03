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
            converted_lines.append("- `{}`: {}".format(entry.type_name, entry.description))
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
                "- `{name}`{details}: {description}".format(
                    name=param.arg_name, details=details, description=param.description
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
            return ["- " + entry for entry in converted]
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
            identifier = " ".join(entry.args[1:])
            if identifier:
                description = "`{}`: {}".format(identifier, description)
            converted.setdefault(heading, []).append(description)
        for heading, entries in converted.items():
            if len(entries) > 1:
                converted[heading] = ["- " + entry for entry in entries]
        return converted

    def _process(self, node: docspec.ApiObject) -> None:
        if not node.docstring:
            return

        lines = []
        components: t.Dict[str, t.List[str]] = {}

        parsed_docstring = docstring_parser.parse(node.docstring.content, self.style)
        self._restore_rest_description_indentation(node.docstring.content, parsed_docstring)
        attribute_params = [
            entry
            for entry in parsed_docstring.params
            if entry.args and entry.args[0].casefold() in ("attribute", "cvar", "ivar", "var")
        ]
        argument_params = [entry for entry in parsed_docstring.params if entry not in attribute_params]
        components["Arguments"] = self._convert_params(argument_params)
        components["Attributes"] = self._convert_params(attribute_params)
        components["Raises"] = self._convert_raises(parsed_docstring.raises)
        returns = [entry for entry in parsed_docstring.many_returns if not entry.is_generator]
        yields = [entry for entry in parsed_docstring.many_returns if entry.is_generator]
        components["Returns"] = self._convert_returns(returns)
        components["Yields"] = self._convert_returns(yields)
        handled = [*parsed_docstring.params, *parsed_docstring.raises, *parsed_docstring.many_returns]
        components.update(self._convert_metadata(parsed_docstring, handled))

        if parsed_docstring.short_description:
            lines.append(parsed_docstring.short_description)
            lines.append("")
        if parsed_docstring.long_description:
            lines.append(parsed_docstring.long_description)
            lines.append("")

        generate_sections_markdown(lines, components)
        node.docstring.content = "\n".join(lines)

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
