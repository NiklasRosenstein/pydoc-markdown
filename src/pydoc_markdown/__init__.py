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
Pydoc-markdown is an extensible framework for generating API documentation,
with a focus on Python source code and the Markdown output format.
"""


from nr.databind.core import Collect, Field, ObjectMapper, Struct, UnionType
from nr.databind.json import JsonModule
from nr.stream import concat
from pydoc_markdown.interfaces import Loader, Processor, Renderer
from pydoc_markdown.reflection import ModuleGraph
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from typing import Union
import logging
import yaml

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '3.1.1'

mapper = ObjectMapper(JsonModule())
logger = logging.getLogger(__name__)


class PydocMarkdown(Struct):
  loaders = Field([Loader], default=lambda: [PythonLoader()])
  processors = Field([Processor], default=lambda: [
    FilterProcessor(), SmartProcessor(), CrossrefProcessor()])
  renderer = Field(Renderer, default=MarkdownRenderer)
  unknown_fields = Field([str], default=[], hidden=True)

  def __init__(self, *args, **kwargs):
    super(PydocMarkdown, self).__init__(*args, **kwargs)
    self.graph = ModuleGraph()
    self.resolver = None

  def load_config(self, data: Union[str, dict]):
    """
    Loads a YAML configuration from *data*.

    Args:
      data (str, dict): If a string is specified, it is treated as the path
        to a YAML file.
    """

    filename = None
    if isinstance(data, str):
      filename = data
      logger.info('Loading configuration file "%s".', filename)
      with open(data) as fp:
        data = yaml.safe_load(fp)

    collector = Collect()
    result = mapper.deserialize(data, type(self), filename=filename, decorations=[collector])
    vars(self).update(vars(result))

    self.unknown_fields = list(concat((str(n.locator.append(u)) for u in n.unknowns)
      for n in collector.nodes))

  def load_modules(self):
    for loader in self.loaders:
      loader.load(self.graph)

  def process(self):
    if self.resolver is None:
      self.resolver = self.renderer.get_resolver(self.graph)
    for processor in self.processors:
      processor.process(self.graph, self.resolver)

  def render(self):
    if self.resolver is None:
      self.resolver = self.renderer.get_resolver(self.graph)
    self.renderer.process(self.graph, self.resolver)
    self.renderer.render(self.graph)
