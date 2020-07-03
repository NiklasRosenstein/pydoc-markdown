
import argparse
from pydoc_markdown.main import cli


__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '0.0.0'


def main():
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(dest='command')
  build = subparsers.add_parser('build')
  build.add_argument('--clean', action='store_true')
  build.add_argument('--site-dir')
  build.add_argument('--config-file')
  build.add_argument('--version', action='store_true')
  args = parser.parse_args()

  if args.version:
    print(__name__, __version__)
    return

  print('>>', args)
  # TODO (@Niklas Rosenstein): Route Mkdocs call to Pydoc-Markdown instead.


if __name__ == '__main__':
  main()
