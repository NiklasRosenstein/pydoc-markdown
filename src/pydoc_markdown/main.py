
"""
Implements the pydoc-markdown CLI.
"""

from pydoc_markdown.parsing import parse_file
from pydoc_markdown.rendering.markdown import MarkdownRenderer

import argparse
import sys


def main(argv=None, prog=None):
  parser = argparse.ArgumentParser(prog=prog)
  parser.add_argument('filename')
  args = parser.parse_args(argv)

  with open(args.filename) as fp:
    module = parse_file(fp.read(), args.filename)

  renderer = MarkdownRenderer()
  renderer.render_recursive(sys.stdout, 1, module)


_entry_point = lambda: sys.exit(main())
