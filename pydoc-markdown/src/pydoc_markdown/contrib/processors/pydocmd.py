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

from pydoc_markdown.interfaces import Processor, Resolver

# TODO @NiklasRosenstein Figure out a way to mark text linking to other
#     objects so that they can be properly handled by the renderer.


@dataclasses.dataclass
class PydocmdProcessor(Processor):
  """
  The Pydoc-Markdown processor for Markdown docstrings. This processor parses docstrings
  formatted like the examples below and turns them into proper Markdown markup.

  Examples:

  ```
  # Arguments

  arg1 (int): The first argument.
  kwargs (dict): Keyword arguments.

  # Raises
  RuntimeError: If something bad happens.
  ValueError: If an invalid argument is specified.

  # Returns
  A value.
  ```

  Renders as:

  # Arguments

  arg1 (int): The first argument.
  kwargs (dict): Keyword arguments.

  # Raises
  RuntimeError: If something bad happens.
  ValueError: If an invalid argument is specified.

  # Returns
  A value.

  @doc:fmt:pydocmd
  """

  def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
    docspec.visit(modules, self._process)

  def _process(self, node: docspec.ApiObject):
    if not getattr(node, 'docstring', None):
      return
    lines = []
    codeblock_opened = False
    current_section = None
    for line in node.docstring.split('\n'):
      if line.startswith("```"):
        codeblock_opened = (not codeblock_opened)
      if not codeblock_opened:
        line, current_section = self._preprocess_line(line, current_section)
      lines.append(line)
    node.docstring = '\n'.join(lines)

  def _preprocess_line(self, line, current_section):
    match = re.match(r'# (.*)$', line)
    if match:
      current_section = match.group(1).strip().lower()
      line = re.sub(r'# (.*)$', r'__\1__\n', line)

    if current_section in ('arguments', 'parameters'):
      style: t.Optional[str] = r'- __\1__:\3'
    elif current_section in ('attributes', 'members', 'raises'):
      style = r'- `\1`:\3'
    elif current_section in ('returns',):
      style = r'`\1`:\3'
    else:
      style = None
    if style:
      #                  | ident  | types     | doc
      line = re.sub(r'\s*([^\\:]+)(\s*\(.+\))?:(.*)$', style, line)

    # Rewrite the argument type in the parentheses.
    if current_section in ('arguments', 'parameters'):
      def sub(m):
        return '__{}__ (`{}`):'.format(m.group(1), m.group(2))
      line = re.sub(r'__(\w+)\s*\((.*?)\)__:', sub, line)

    return line, current_section
