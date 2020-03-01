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

from . import PydocMarkdown
import argparse
import click
import sys


def error(*args):
  print(*args, file=sys.stderr)
  exit(1)


@click.command()
@click.option('--config', '-c', help='Path to the YAML configuration '
    'file. Defaults to pydoc-markdown.yml')
@click.option('--modules', multiple=True, help='One or more module names '
    'to generate API documentation for. If specified, the configuration '
    'file will not be read, but instead the default configuration is used.')
@click.option('--search-path', multiple=True, help='One or more search paths for '
  'the Python loader. Only used in combination with --modules')
def main(config, modules, search_path):
  if config and modules:
    error('--modules cannot be combined with --config')

  pydocmd = PydocMarkdown()
  if modules:
    config = {'loaders': [{
      'type': 'python',
      'modules': modules,
      'search_path': search_path
    }]}

  config = pydocmd.load_config(config or 'pydoc-markdown.yml')
  if not config.loaders:
    error('no loaders configured')

  pydocmd.load_module_graph()
  pydocmd.process()
  pydocmd.render()


_entry_point = lambda: sys.exit(main())


if __name__ == '__main__':
  sys.exit(_entry_point())
