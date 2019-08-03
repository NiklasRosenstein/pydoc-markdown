
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

  def load(self, interface):
    instance = load_implementation(interface, self.type)()
    instance.config = extract(self.options, instance.get_config_class())
    return instance


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
      with open(filename) as fp:
        data = yaml.safe_load(fp)
    self.config = extract(data, PydocMarkdownConfig)
    self.loaders = [x.load(Loader) for x in self.config.loaders]
    self.processors = [x.load(Processor) for x in self.config.processors]
    self.renderer = self.config.renderer.load(Renderer)

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
    'file. Defaults to pydoc-markdown.yml', default='pydoc-markdown.yml')
  args = parser.parse_args(argv)

  pydocmd = PydocMarkdown()
  pydocmd.load_config(args.config)
  if not pydocmd.loaders:
    parser.error('no loaders configured')
  pydocmd.load_module_graph()
  pydocmd.process()
  pydocmd.render()


_entry_point = lambda: sys.exit(main())
