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
Provides a processor that implements various filter capabilities.
"""

from nr.databind.core import Field, Struct
from nr.interface import implements
from pydoc_markdown.interfaces import Processor
from pydoc_markdown.reflection import ModuleGraph


@implements(Processor)
class FilterProcessor(Struct):
  """
  The `filter` processor removes module and class members based on certain
  criteria.

  # Example

  ```py
  - type: filter
    expression: not name.startswith('_') and default()
  ```
  """

  expression = Field(str, default=None)
  documented_only = Field(bool, default=True)
  exclude_private = Field(bool, default=True)
  exclude_special = Field(bool, default=True)
  include_root_objects = Field(bool, default=True)

  SPECIAL_MEMBERS = ('__path__', '__annotations__', '__name__', '__all__')

  def process(self, graph, _resolver):
    graph.visit(self._process_member)

  def _process_member(self, node):
    def _check(node):
      if self.documented_only and not node.docstring:
        return False
      if self.exclude_private and node.name.startswith('_') and not node.name.endswith('_'):
        return False
      if self.exclude_special and node.name in self.SPECIAL_MEMBERS:
        return False
      return True

    if self.expression:
      scope = {'name': node.name, 'node': node, 'default': _check}
      if not eval(self.expression, scope):  # pylint: disable=eval-used
        node.visible = False

    if self.include_root_objects and (
        not node.parent or isinstance(node.parent, ModuleGraph)):
      return

    if not _check(node):
      node.visible = False
