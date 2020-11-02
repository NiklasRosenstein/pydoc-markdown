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


from nr.databind.core import Collect, Field, FieldName, ObjectMapper, Struct, UnionType
from nr.databind.json import JsonModule
from nr.stream import concat
from pydoc_markdown.interfaces import Context, Loader, Processor, Renderer, Resolver, Builder
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.util import ytemplate
from typing import List, Union
import docspec
import logging
import os
import subprocess
import yaml

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '3.6.1'

mapper = ObjectMapper(JsonModule())
logger = logging.getLogger(__name__)


class PydocMarkdown(Struct):
  """
  This object represents the main configuration for Pydoc-Markdown.
  """

  #: A list of loader implementations that load #docspec.Module#s.
  #: Defaults to #PythonLoader.
  loaders = Field([Loader], default=lambda: [PythonLoader()])

  #: A list of processor implementations that modify #docspec.Module#s. Defaults
  #: to #FilterProcessor, #SmartProcessor and #CrossrefProcessor.
  processors = Field([Processor], default=lambda: [
    FilterProcessor(), SmartProcessor(), CrossrefProcessor()])

  #: A renderer for #docspec.Module#s. Defaults to #MarkdownRenderer.
  renderer = Field(Renderer, default=MarkdownRenderer)

  #: Hooks that can be executed at certain points in the pipeline. The commands
  #: are executed with the current `SHELL`.
  hooks = Field({
    'pre_render': Field([str], FieldName('pre-render'), default=list),
    'post_render': Field([str], FieldName('post-render'), default=list),
  }, default=Field.DEFAULT_CONSTRUCT)

  # Hidden fields are filled at a later point in time and are not (de-) serialized.
  unknown_fields = Field([str], default=list, hidden=True)
  resolver = Field(Resolver, default=None, hidden=True)

  def __init__(self, *args, **kwargs) -> None:
    super(PydocMarkdown, self).__init__(*args, **kwargs)
    self.resolver = None
    self._context = None

  def load_config(self, data: Union[str, dict]) -> None:
    """
    Loads a YAML configuration from *data*.

    :param data: Nested structurre or the path to a YAML configuration file.
    """

    filename = None
    if isinstance(data, str):
      filename = data
      logger.info('Loading configuration file "%s".', filename)
      data = ytemplate.load(filename, {'env': ytemplate.Attributor(os.environ)})

    collector = Collect()
    result = mapper.deserialize(data, type(self), filename=filename, decorations=[collector])
    vars(self).update(vars(result))

    self.unknown_fields = list(concat((str(n.locator.append(u)) for u in n.unknowns)
      for n in collector.nodes))

  def init(self, context: Context) -> None:
    """
    Initialize all plugins with the specified *context*. Cannot be called multiple times.
    If omitted, the plugins will be initialized with a default context before the load,
    process or render phase.
    """

    if self._context:
      raise RuntimeError('already initialized')
    self._context = context
    logger.debug('Initializing plugins with context %r', context)
    for loader in self.loaders:
      loader.init(context)
    for processor in self.processors:
      processor.init(context)
    self.renderer.init(context)

  def ensure_initialized(self) -> None:
    if not self._context:
      self.init(Context(directory='.'))

  def load_modules(self) -> List[docspec.Module]:
    """
    Loads modules via the #loaders.
    """

    logger.info('Loading modules.')
    self.ensure_initialized()
    modules = []
    for loader in self.loaders:
      modules.extend(loader.load())
    return modules

  def process(self, modules: List[docspec.Module]) -> None:
    """
    Process modules via the #processors.
    """

    self.ensure_initialized()
    if self.resolver is None:
      self.resolver = self.renderer.get_resolver(modules)
    for processor in self.processors:
      processor.process(modules, self.resolver)

  def render(self, modules: List[docspec.Module], run_hooks: bool = True) -> None:
    """
    Render modules via the #renderer.
    """

    self.ensure_initialized()
    if run_hooks:
      self.run_hooks('pre-render')
    if self.resolver is None:
      self.resolver = self.renderer.get_resolver(modules)
    self.renderer.process(modules, self.resolver)
    self.renderer.render(modules)
    if run_hooks:
      self.run_hooks('post-render')

  def build(self, site_dir: str=None) -> None:
    if not Builder.provided_by(self.renderer):
      name = type(self.renderer).__name__
      raise NotImplementedError('Renderer "{}" does not support building'.format(name))
    self.ensure_initialized()
    self.renderer.build(site_dir)

  def run_hooks(self, hook_name: str) -> None:
    for command in getattr(self.hooks, hook_name.replace('-', '_')):
      subprocess.check_call(command, shell=True, cwd=self._context.directory)
