
"""
Implements the pydoc-markdown CLI.
"""

import argparse
import nr.config
import sys

from nr.types import record
from pydoc_markdown.parse import parse_file
from pydoc_markdown.preprocessors import load_preprocessor
from pydoc_markdown.renderers import load_renderer


class _ExtensionConfig(nr.config.Partial):
  type = nr.config.Field(str)
  options = nr.config.Field.wildcard(str, object)


class PydocMarkdownConfig(nr.config.Partial):
  preprocessor = nr.config.Field(_ExtensionConfig, default=lambda: _ExtensionConfig('pydocmd', {}))
  renderer = nr.config.Field(_ExtensionConfig, default=lambda: _ExtensionConfig('markdown', {}))
  files = nr.config.Field((list, str))


def main(argv=None, prog=None):
  parser = argparse.ArgumentParser(prog=prog)
  parser.add_argument('-c', '--config', help='Path to the YAML configuration '
    'file. Defaults to pydoc-markdown.yml', default='pydoc-markdown.yml')
  args = parser.parse_args(argv)

  config = nr.config.extract(PydocMarkdownConfig, args.config)
  preprocessor = load_preprocessor(config.preprocessor.type)(config.preprocessor.options)
  renderer = load_renderer(config.renderer.type)(config.renderer.options)

  modules = []
  for filename in config.files:
    with open(filename) as fp:
      modules.append(parse_file(fp.read(), filename))

  for module in modules:
    preprocessor.preprocess_tree(module)
  renderer.render(modules)


_entry_point = lambda: sys.exit(main())
