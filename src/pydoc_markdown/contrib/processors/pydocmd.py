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

"""
Provides the #PydocmdProcessor class which converts the Pydoc-Markdown
highlighting syntax into Markdown.
"""

import re

from nr.databind.core import Field, Struct
from nr.interface import implements
from pydoc_markdown.interfaces import Processor

# TODO @NiklasRosenstein Figure out a way to mark text linking to other
#     objects so that they can be properly handled by the renderer.

@implements(Processor)
class PydocmdProcessor(Struct):

  def process(self, graph):
    graph.visit(self._process_node)

  def _process_node(self, node):
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
    node.docstring = self._preprocess_refs('\n'.join(lines))

  def _preprocess_line(self, line, current_section):
    match = re.match(r'# (.*)$', line)
    if match:
      current_section = match.group(1).strip().lower()
      line = re.sub(r'# (.*)$', r'__\1__\n', line)

    if current_section in ('arguments', 'parameters'):
      style = r'- __\1__:\3'
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

  def _preprocess_refs(self, content):
    def handler(match):
      ref = match.group('ref')
      parens = match.group('parens') or ''
      has_trailing_dot = False
      if not parens and ref.endswith('.'):
        ref = ref[:-1]
        has_trailing_dot = True
      result = '`{}`'.format(ref + parens)
      if has_trailing_dot:
        result += '.'
      return (match.group('prefix') or '') + result
    return re.sub(r'(?P<prefix>^| |\t)#(?P<ref>[\w\d\._]+)(?P<parens>\(\))?', handler, content)
