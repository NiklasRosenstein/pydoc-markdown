
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
  build.add_argument('--version', action='store_true',
    help='Prints the version of the package. This is mainly used to test the hook that is '
         'installed with this packages which catches "python -m mkdocs build".')
  args = parser.parse_args()

  if args.version:
    print(__name__, __version__)
    return

  # TODO (@NiklasRosenstein): Pass --clean and --config-file as well?
  cli(['--build', '--site-dir', args.site_dir])


if __name__ == '__main__':
  main()
