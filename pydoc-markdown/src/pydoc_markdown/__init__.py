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

import dataclasses
import logging
import os
import subprocess
import toml
import typing as t

import databind.core.annotations as A
import databind.json
import docspec

from pydoc_markdown.interfaces import Context, Loader, Processor, Renderer, Resolver, Builder
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.util import ytemplate


__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '4.1.5'

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Hooks:
  pre_render: t.List[str] = dataclasses.field(default_factory=list, metadata={'alias': 'pre-render'})
  post_render: t.List[str] = dataclasses.field(default_factory=list, metadata={'alias': 'post-render'})


@dataclasses.dataclass
class PydocMarkdown:
  """
  This object represents the main configuration for Pydoc-Markdown.
  """

  #: A list of loader implementations that load #docspec.Module#s.
  #: Defaults to #PythonLoader.
  loaders: t.List[Loader] = dataclasses.field(default_factory=lambda: [PythonLoader()])

  #: A list of processor implementations that modify #docspec.Module#s. Defaults
  #: to #FilterProcessor, #SmartProcessor and #CrossrefProcessor.
  processors: t.List[Processor] = dataclasses.field(default_factory=lambda: [
    FilterProcessor(), SmartProcessor(), CrossrefProcessor()])

  #: A renderer for #docspec.Module#s. Defaults to #MarkdownRenderer.
  renderer: Renderer = dataclasses.field(default_factory=MarkdownRenderer)

  #: Hooks that can be executed at certain points in the pipeline. The commands
  #: are executed with the current `SHELL`.
  hooks: Hooks = dataclasses.field(default_factory=Hooks)

  # Hidden fields are filled at a later point in time and are not (de-) serialized.
  unknown_fields: t.List[str] = dataclasses.field(default_factory=list)

  def __post_init__(self) -> None:
    self.resolver: t.Optional[Resolver] = None
    self._context: t.Optional[Context] = None

  def load_config(self, data: t.Union[str, dict]) -> None:
    """
    Loads the configuration from a nested data structure or filename as specified per the *data*
    argument. If a filename is specified, it may be a JSON, YAML or TOML file. If the name of the
    TOML file is `pyproject.yoml`, the configuration will be read from the `[tool.pydoc-markdown]`
    section.

    :param data: A nested structure or the path to a configuration file.
    """

    filename = None
    if isinstance(data, str):
      filename = data
      logger.info('Loading configuration file "%s".', filename)
      if filename.endswith('.toml'):
        data = toml.load(filename)
      else:
        data = ytemplate.load(filename, {'env': ytemplate.Attributor(os.environ)})
      if filename == 'pyproject.toml':
        data = data['tool']['pydoc-markdown']

    unknown_keys = A.collect_unknowns()
    result = databind.json.new_mapper().deserialize(
      data,
      type(self),
      filename=filename,
      settings=[unknown_keys()])
    vars(self).update(vars(result))

    for loc, keys in unknown_keys:
      for key in keys:
        self.unknown_fields.append(str(loc.push_unknown(key).format(loc.Format.PLAIN)))

    #self.unknown_fields = list(concat((str(n.locator.append(u)) for u in n.unknowns)
    #  for n in collector.nodes))

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

  def load_modules(self) -> t.List[docspec.Module]:
    """
    Loads modules via the #loaders.
    """

    logger.info('Loading modules.')
    self.ensure_initialized()
    modules = []
    for loader in self.loaders:
      modules.extend(loader.load())
    return modules

  def process(self, modules: t.List[docspec.Module]) -> None:
    """
    Process modules via the #processors.
    """

    self.ensure_initialized()
    if self.resolver is None:
      self.resolver = self.renderer.get_resolver(modules)
    for processor in self.processors:
      processor.process(modules, self.resolver)

  def render(self, modules: t.List[docspec.Module], run_hooks: bool = True) -> None:
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

  def build(self, site_dir: str) -> None:
    if not isinstance(self.renderer, Builder):
      name = type(self.renderer).__name__
      raise NotImplementedError('Renderer "{}" does not support building'.format(name))
    self.ensure_initialized()
    self.renderer.build(site_dir)

  def run_hooks(self, hook_name: str) -> None:
    assert self._context is not None

    # Remove the __PYVENV_LAUNCHER__ environment variable. This is needed if you are in a virtualenv and the hook
    # tries to invoke a script installed into a _different_ virtualenv. Otherwise, that script's execution of the
    # Python `site` module will set the `sys.prefix` the prefix of your terminal's activated virtualenv. The prefix
    # is then used to find site-packages, and thus none of the site-packages from the script's actual prefix are
    # detected.
    env = os.environ.copy()
    env.pop('__PYVENV_LAUNCHER__', None)

    for command in getattr(self.hooks, hook_name.replace('-', '_')):
      subprocess.check_call(command, shell=True, cwd=self._context.directory, env=env)
