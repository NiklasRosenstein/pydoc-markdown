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
import re
import typing as t

import docspec

from pydoc_markdown.contrib.processors.sphinx import generate_sections_markdown
from pydoc_markdown.interfaces import Processor, Resolver


@dataclasses.dataclass
class GoogleProcessor(Processor):
    """
    This class implements the preprocessor for Google and PEP 257 docstrings. It converts
    docstrings formatted in the Google docstyle to Markdown syntax.

    References:

    * https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
    * https://www.python.org/dev/peps/pep-0257/

    Example:

    ```
    Attributes:
        module_level_variable1 (int): Module level variables may be documented in
            either the ``Attributes`` section of the module docstring, or in an
            inline docstring immediately following the variable.

            Either form is acceptable, but the two should not be mixed. Choose
            one convention to document module level variables and be consistent
            with it.

    Todo:
        * For module TODOs
        * You have to also use ``sphinx.ext.todo`` extension
    ```

    Renders as:

    Attributes:
        module_level_variable1 (int): Module level variables may be documented in
            either the ``Attributes`` section of the module docstring, or in an
            inline docstring immediately following the variable.

            Either form is acceptable, but the two should not be mixed. Choose
            one convention to document module level variables and be consistent
            with it.

    Todo:
        * For module TODOs
        * You have to also use ``sphinx.ext.todo`` extension

    Relative indentation in section bodies is preserved. In `Example:` and `Examples:` sections, an indented body
    without a fenced code block remains a Markdown literal block. Structural Google-style indentation is removed
    from fenced code blocks so that their fences render correctly.

    @doc:fmt:google
    """

    _param_res = [
        re.compile(r"^(?P<param>\S+):\s+(?P<desc>.+)$"),
        re.compile(r"^(?P<param>\S+)\s+\((?P<type>[^)]+)\):\s+(?P<desc>.+)$"),
        re.compile(r"^(?P<param>\S+)\s+--\s+(?P<desc>.+)$"),
        re.compile(r"^(?P<param>\S+)\s+\{\[(?P<type>\S+)\]\}\s+--\s+(?P<desc>.+)$"),
        re.compile(r"^(?P<param>\S+)\s+\{(?P<type>\S+)\}\s+--\s+(?P<desc>.+)$"),
    ]

    _keywords_map = {
        "Args:": "Arguments",
        "Arguments:": "Arguments",
        "Attributes:": "Attributes",
        "Example:": "Example",
        "Examples:": "Examples",
        "Keyword Args:": "Arguments",
        "Keyword Arguments:": "Arguments",
        "Methods:": "Methods",
        "Note:": "Notes",
        "Notes:": "Notes",
        "Other Parameters:": "Arguments",
        "Parameters:": "Arguments",
        "Return:": "Returns",
        "Returns:": "Returns",
        "Raises:": "Raises",
        "References:": "References",
        "See Also:": "See Also",
        "Todo:": "Todo",
        "Warning:": "Warnings",
        "Warnings:": "Warnings",
        "Warns:": "Warns",
        "Yield:": "Yields",
        "Yields:": "Yields",
    }

    def check_docstring_format(self, docstring: str) -> bool:
        for section_name in self._keywords_map:
            if section_name in docstring:
                return True
        return False

    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        docspec.visit(modules, self._process)

    @staticmethod
    def _get_indentation(line: str) -> int:
        leading_whitespace = line[: len(line) - len(line.lstrip())]
        return len(leading_whitespace.expandtabs(4))

    @classmethod
    def _remove_indentation(cls, line: str, indentation: int) -> str:
        leading_length = len(line) - len(line.lstrip())
        leading_whitespace = line[:leading_length].expandtabs(4)
        return leading_whitespace[min(len(leading_whitespace), indentation) :] + line[leading_length:]

    def _format_section(self, keyword: str, raw_lines: t.List[str]) -> t.List[str]:
        section_indent = min((self._get_indentation(line) for line in raw_lines if line.strip()), default=0)
        has_codeblock = any(line.lstrip().startswith("```") for line in raw_lines)
        is_example = keyword in ("Example", "Examples")

        # An indented, unfenced Examples section is a Markdown literal block. Keep its indentation intact.
        if is_example and not has_codeblock:
            return [line if line else "  " for line in raw_lines]

        result: t.List[str] = []
        in_codeblock = False
        codeblock_indent = 0
        after_parameter = False
        continuation_indent: t.Optional[int] = None

        for raw_line in raw_lines:
            line = raw_line.strip()
            normalized_line = self._remove_indentation(raw_line, section_indent).rstrip()

            if line.startswith("```"):
                if not in_codeblock:
                    codeblock_indent = min(section_indent, self._get_indentation(raw_line))
                in_codeblock = not in_codeblock
                result.append(self._remove_indentation(raw_line, codeblock_indent).rstrip())
                continue

            if in_codeblock:
                result.append(self._remove_indentation(raw_line, codeblock_indent).rstrip())
                continue

            param_match = None
            for param_re in self._param_res:
                param_match = param_re.match(line)
                if param_match:
                    if "type" in param_match.groupdict():
                        result.append("- `{param}` _{type}_ - {desc}".format(**param_match.groupdict()))
                    else:
                        result.append("- `{param}` - {desc}".format(**param_match.groupdict()))
                    after_parameter = True
                    continuation_indent = None
                    break

            if param_match:
                continue

            if not line:
                result.append("  ")
                continue

            if after_parameter:
                line_indent = self._get_indentation(raw_line)
                if continuation_indent is None:
                    continuation_indent = line_indent
                relative_indent = max(line_indent - continuation_indent, 0)
                result.append("  " + " " * relative_indent + line)
            else:
                result.append("  " + normalized_line)

        return result

    def _process(self, node: docspec.ApiObject) -> None:
        if not node.docstring:
            return

        lines: t.List[str] = []
        current_lines: t.List[str] = []
        in_codeblock = False
        keyword: t.Optional[str] = None

        def _commit() -> None:
            if keyword:
                generate_sections_markdown(lines, {keyword: self._format_section(keyword, current_lines)})
            else:
                lines.extend(current_lines)
            current_lines.clear()

        for line in node.docstring.content.split("\n"):
            stripped_line = line.strip()
            if stripped_line.startswith("```"):
                in_codeblock = not in_codeblock
                current_lines.append(line)
                continue

            if in_codeblock:
                current_lines.append(line)
                continue

            if stripped_line in self._keywords_map:
                _commit()
                keyword = self._keywords_map[stripped_line]
                continue

            if keyword is None:
                lines.append(stripped_line)
                continue

            current_lines.append(line)

        _commit()
        node.docstring.content = "\n".join(lines)
