
"""
Implements the pydoc-markdown CLI.
"""

from pydoc_markdown.parse import parse_file
from pydoc_markdown.render.markdown import MarkdownRenderer
from pydoc_markdown.preprocessors.pydoc_md import PydocMdPreprocessor
from pydoc_markdown.preprocessors.sphinx import SphinxPreprocessor

import argparse
import sys


def main(argv=None, prog=None):
  parser = argparse.ArgumentParser(prog=prog)
  parser.add_argument('filename')
  parser.add_argument('--sphinx', action='store_true',
    help='Enable Sphinx docstring support.')
  args = parser.parse_args(argv)

  with open(args.filename) as fp:
    module = parse_file(fp.read(), args.filename)

  preproc = SphinxPreprocessor() if args.sphinx else PydocMdPreprocessor()
  preproc.preprocess_tree(module)

  renderer = MarkdownRenderer()
  renderer.render_recursive(sys.stdout, 1, module)


_entry_point = lambda: sys.exit(main())
