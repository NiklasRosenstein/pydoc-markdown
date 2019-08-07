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
Implements the pydoc-markdown CLI.
"""

import argparse
import sys
import yaml

from nr.types import record
from nr.types.structured import Field, Object, WildcardField, extract
from pydoc_markdown.interfaces import Loader, Processor, Renderer, load_implementation
from pydoc_markdown.reflection import ModuleGraph


class _ExtensionConfig(Object):
  type = Field(str)
  options = WildcardField(object)


class PydocMarkdownConfig(Object):
  loaders = Field([_ExtensionConfig], default=list)
  processors = Field([_ExtensionConfig], default=lambda: [_ExtensionConfig('pydocmd', {})])
  renderer = Field(_ExtensionConfig, default=lambda: _ExtensionConfig('markdown', {}))


class PydocMarkdown(object):
  """
  This class wraps all the functionality provided by the command-line.
  """

  def __init__(self):
    self.config = PydocMarkdownConfig()
    self.loaders = []
    self.processors = []
    self.renderer = None
    self.graph = ModuleGraph()

  def load_config(self, data):
    """
    Loads the configuration. *data* be a string pointing to a YAML file or
    a dictionary.
    """

    if isinstance(data, str):
      with open(data) as fp:
        data = yaml.safe_load(fp)
    self.config = extract(data, PydocMarkdownConfig)
    self.loaders = [Loader.make_instance(x.type, x.options) for x in self.config.loaders]
    self.processors = [Processor.make_instance(x.type, x.options) for x in self.config.processors]
    self.renderer = Renderer.make_instance(self.config.renderer.type, self.config.renderer.options)

  def load_module_graph(self):
    for loader in self.loaders:
      loader.load(loader.config, self.graph)

  def process(self):
    for processor in self.processors:
      processor.process(processor.config, self.graph)

  def render(self):
    self.renderer.process(self.renderer.config, self.graph)
    self.renderer.render(self.renderer.config, self.graph)


def main(argv=None, prog=None):
  parser = argparse.ArgumentParser(prog=prog)
  parser.add_argument('-c', '--config', help='Path to the YAML configuration '
    'file. Defaults to pydoc-markdown.yml', default=None)
  parser.add_argument('--modules', nargs='+', help='One or more module names '
    'to generate API documentation for. If specified, the configuration file '
    'will not be read, but instead the default configuration is used.')
  parser.add_argument('--search-path', nargs='+', help='One or more search '
    'paths for the Python loader. Only used in combination with --modules')
  parser.add_argument('--path-to', help='Just a helper, will be removed.')
  args = parser.parse_args(argv)

  if args.path_to:
    import imp
    print(imp.find_module(args.path_to)[1])
    exit()

  if args.config and args.modules:
    parser.error('--modules cannot be combined with --config')

  pydocmd = PydocMarkdown()
  if args.modules:
    args.config = {'loaders': [{
      'type': 'python',
      'modules': args.modules,
      'search_path': args.search_path
    }]}

  pydocmd.load_config(args.config or 'pydoc-markdown.yml')
  if not pydocmd.loaders:
    parser.error('no loaders configured')

  pydocmd.load_module_graph()
  pydocmd.process()
  pydocmd.render()


_entry_point = lambda: sys.exit(main())
