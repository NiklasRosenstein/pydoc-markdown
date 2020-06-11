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

from nr.databind.core import Field, Struct
from nr.interface import implements, override
from pydoc_markdown.interfaces import Processor
import docspec


@implements(Processor)
class FilterProcessor(Struct):
  """
  The `filter` processor removes module and class members based on certain criteria.

  # Example

  ```py
  - type: filter
    expression: not name.startswith('_') and default()
    documented_only: false
  ```
  """

  expression = Field(str, default=None)
  documented_only = Field(bool, default=True)
  exclude_private = Field(bool, default=True)
  exclude_special = Field(bool, default=True)
  do_not_filter_modules = Field(bool, default=True)

  SPECIAL_MEMBERS = ('__path__', '__annotations__', '__name__', '__all__')

  @override
  def process(self, modules, _resolver):
    def m(obj):
      return self._match(obj)
    docspec.filter_visit(modules, m, order='post')

  def _match(self, obj: docspec.ApiObject) -> bool:
    if getattr(obj, 'members', []):
      return True
    if self.do_not_filter_modules and isinstance(obj, docspec.Module):
      return True
    if self.documented_only and not obj.docstring:
      return False
    if self.exclude_private and obj.name.startswith('_') and not obj.name.endswith('_'):
      return False
    if self.exclude_special and obj.name in self.SPECIAL_MEMBERS:
      return False
    if self.expression:
      scope = {'name': obj.name, 'obj': obj, 'default': _check}
      if not eval(self.expression, scope):  # pylint: disable=eval-used
        return False
    return True
