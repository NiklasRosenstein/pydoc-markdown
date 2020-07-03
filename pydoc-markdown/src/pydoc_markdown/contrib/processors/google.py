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

from nr.databind.core import Struct
from nr.interface import implements, override
from pydoc_markdown.contrib.processors.sphinx import generate_sections_markdown
from pydoc_markdown.interfaces import Processor, Resolver
from typing import List, Optional
import docspec
import re


@implements(Processor)
class GoogleProcessor(Struct):
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

  @doc:fmt:google
  """

  _param_res = [
    re.compile(r'^(?P<param>\S+):\s+(?P<desc>.+)$'),
    re.compile(r'^(?P<param>\S+)\s+\((?P<type>[^)]+)\):\s+(?P<desc>.+)$'),
    re.compile(r'^(?P<param>\S+)\s+--\s+(?P<desc>.+)$'),
    re.compile(
      r'^(?P<param>\S+)\s+\{\[(?P<type>\S+)\]\}\s+--\s+(?P<desc>.+)$'),
    re.compile(
      r'^(?P<param>\S+)\s+\{(?P<type>\S+)\}\s+--\s+(?P<desc>.+)$'),
  ]

  _keywords_map = {
    'Args:': 'Arguments',
    'Arguments:': 'Arguments',
    'Attributes:': 'Attributes',
    'Example:': 'Example',
    'Examples:': 'Examples',
    'Keyword Args:': 'Arguments',
    'Keyword Arguments:': 'Arguments',
    'Methods:': 'Methods',
    'Note:': 'Notes',
    'Notes:': 'Notes',
    'Other Parameters:': 'Arguments',
    'Parameters:': 'Arguments',
    'Return:': 'Returns',
    'Returns:': 'Returns',
    'Raises:': 'Raises',
    'References:': 'References',
    'See Also:': 'See Also',
    'Todo:': 'Todo',
    'Warning:': 'Warnings',
    'Warnings:': 'Warnings',
    'Warns:': 'Warns',
    'Yield:': 'Yields',
    'Yields:': 'Yields',
  }

  def check_docstring_format(self, docstring: str) -> bool:
    for section_name in self._keywords_map:
      if section_name in docstring:
        return True
    return False

  @override
  def process(self, modules: List[docspec.Module], resolver: Optional[Resolver]) -> None:
    docspec.visit(modules, self._process)

  def _process(self, node: docspec.ApiObject):
    if not node.docstring:
      return

    lines = []
    current_lines = []
    in_codeblock = False
    keyword = None

    def _commit():
      if keyword:
        generate_sections_markdown(lines, {keyword: current_lines})
      else:
        lines.extend(current_lines)
      current_lines.clear()

    for line in node.docstring.split('\n'):
      if line.startswith("```"):
        in_codeblock = not in_codeblock
        current_lines.append(line)
        continue

      if in_codeblock:
        current_lines.append(line)
        continue

      line = line.strip()
      if line in self._keywords_map:
        _commit()
        keyword = self._keywords_map[line]
        continue

      if keyword is None:
        lines.append(line)
        continue

      for param_re in self._param_res:
        param_match = param_re.match(line)
        if param_match:
          if 'type' in param_match.groupdict():
            current_lines.append(
              '- `{param}` _{type}_ - {desc}'.format(**param_match.groupdict()))
          else:
            current_lines.append(
              '- `{param}` - {desc}'.format(**param_match.groupdict()))
          break

      if not param_match:
        current_lines.append('  {line}'.format(line=line))

    _commit()
    node.docstring = '\n'.join(lines)
