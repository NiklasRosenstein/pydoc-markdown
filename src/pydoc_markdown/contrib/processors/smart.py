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
from pydoc_markdown.interfaces import Processor, Resolver
from pydoc_markdown.contrib.processors.google import GoogleProcessor
from pydoc_markdown.contrib.processors.pydocmd import PydocmdProcessor
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor
from typing import List, Optional
import docspec


@implements(Processor)
class SmartProcessor(Struct):
  """
  This processor picks the #GoogleProcessor, #SphinxProcessor or #PydocmdProcessor after
  guessing which is appropriate from the syntax it finds in the docstring.
  """

  google = Field(GoogleProcessor, default=GoogleProcessor)
  pydocmd = Field(PydocmdProcessor, default=PydocmdProcessor)
  sphinx = Field(SphinxProcessor, default=SphinxProcessor)

  @override
  def process(self, modules: List[docspec.Module], resolver: Optional[Resolver]) -> None:
    docspec.visit(modules, self._process)

  def _process(self, obj: docspec.ApiObject):
    if not obj.docstring:
      return None

    for name in ('google', 'pydocmd', 'sphinx'):
      indicator = '@doc:fmt:' + name
      if indicator in obj.docstring:
        obj.docstring = obj.docstring.replace(indicator, '')
        return getattr(self, name)._process(obj)

    if self.sphinx.check_docstring_format(obj.docstring):
      return self.sphinx._process(obj)
    if self.google.check_docstring_format(obj.docstring):
      return self.google._process(obj)
    return self.pydocmd._process(obj)
