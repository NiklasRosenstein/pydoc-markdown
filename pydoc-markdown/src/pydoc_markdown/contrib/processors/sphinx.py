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
from pydoc_markdown.interfaces import Processor, Resolver
from typing import List, Optional
import docspec
import re


def generate_sections_markdown(lines, sections):
  for key, section in sections.items():
    if lines and lines[-1]:
      lines.append('')

    lines.extend(['**{}**:'.format(key), ''])  # add an extra line because of markdown syntax
    lines.extend(section)


@implements(Processor)
class SphinxProcessor(Struct):
  """
  This processor parses ReST/Sphinx-style function documentation and converts it into
  Markdown syntax.

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

  def check_docstring_format(self, docstring: str) -> bool:
    return ':param' in docstring or ':return' in docstring or \
      ':raise' in docstring

  @override
  def process(self, modules: List[docspec.Module], resolver: Optional[Resolver]) -> None:
    docspec.visit(modules, self._process)

  def _process(self, node):
    if not node.docstring:
      return

    lines = []
    in_codeblock = False
    keyword = None
    components = {}

    for line in node.docstring.split('\n'):
      line = line.strip()

      if line.startswith("```"):
        in_codeblock = not in_codeblock

      line_codeblock = line.startswith('    ')

      if not in_codeblock and not line_codeblock:
        match = re.match(r'\s*:(?:arg|argument|param|parameter)\s+(\w+)\s*:(.*)?$', line)
        if match:
          keyword = 'Arguments'
          param = match.group(1)
          text = match.group(2)
          text = text.strip()

          component = components.setdefault(keyword, [])
          component.append('- `{}`: {}'.format(param, text))
          continue

        match = re.match(r'\s*:(?:return|returns)\s*:(.*)?$', line)
        if match:
          keyword = 'Returns'
          text = match.group(1)
          text = text.strip()

          component = components.setdefault(keyword, [])
          component.append(text)
          continue

        match = re.match('\\s*:(?:raises|raise)\\s+(\\w+)\\s*:(.*)?$', line)
        if match:
          keyword = 'Raises'
          exception = match.group(1)
          text = match.group(2)
          text = text.strip()

          component = components.setdefault(keyword, [])
          component.append('- `{}`: {}'.format(exception, text))
          continue

      if keyword is not None:
        components[keyword].append(line)
      else:
        lines.append(line)

    generate_sections_markdown(lines, components)
    node.docstring = '\n'.join(lines)
