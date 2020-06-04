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
from nr.interface import implements
from pydoc_markdown.interfaces import Processor
from pydoc_markdown.contrib.processors.google import GoogleProcessor
from pydoc_markdown.contrib.processors.pydocmd import PydocmdProcessor
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor


@implements(Processor)
class SmartProcessor(Struct):
  google = Field(GoogleProcessor, default=GoogleProcessor)
  pydocmd = Field(PydocmdProcessor, default=PydocmdProcessor)
  sphinx = Field(SphinxProcessor, default=SphinxProcessor)

  def process(self, graph, _resolver):
    """
    Preprocesses a given section into its components.
    """

    graph.visit(self.process_node)

  def process_node(self, node):
    if not node.docstring:
      return None
    if self.sphinx.check_docstring_format(node.docstring):
      return self.sphinx.process_node(node)
    if self.google.check_docstring_format(node.docstring):
      return self.google.process_node(node)
    return self.pydocmd.process_node(node)
