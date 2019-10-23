# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function
from .document import Index
from .imp import import_object, dir_object
from argparse import ArgumentParser

import atexit
import os
import shutil
import signal
import subprocess
import sys
import yaml

PYDOCMD_CONFIG = 'pydocmd.yml'
parser = ArgumentParser()
parser.add_argument('command', choices=['generate', 'build', 'gh-deploy',
                                        'json', 'new', 'serve', 'simple'])
parser.add_argument('subargs', nargs='...')


def read_config():
  """
  Reads and preprocesses the pydoc-markdown configuration file.
  """

  with open(PYDOCMD_CONFIG) as fp:
    config = yaml.safe_load(fp)
  return default_config(config)


def default_config(config):
  args = parser.parse_args()
  config.setdefault('docs_dir', 'sources')
  config.setdefault('gens_dir', '_build/pydocmd')
  config.setdefault('site_dir', '_build/site')
  if args.command == 'simple':
    config.setdefault('headers', 'markdown')
  else:
    config.setdefault('headers', 'html')
  config.setdefault('theme', 'readthedocs')
  config.setdefault('loader', 'pydocmd.loader.PythonLoader')
  config.setdefault('preprocessor', 'pydocmd.preprocessors.simple.Preprocessor')
  config.setdefault('additional_search_paths', [])
  return config


def write_temp_mkdocs_config(inconf):
  """
  Generates a configuration for MkDocs on-the-fly from the pydoc-markdown
  configuration and makes sure it gets removed when this program exists.
  """
  ignored_keys = ('gens_dir', 'pages', 'headers', 'generate', 'loader',
                  'preprocessor', 'additional_search_paths')

  config = {k: v for k, v in inconf.items() if k not in ignored_keys}
  config['docs_dir'] = inconf['gens_dir']
  if 'pages' in inconf:
      config['nav'] = inconf['pages']

  with open('mkdocs.yml', 'w') as fp:
    yaml.dump(config, fp)

  atexit.register(lambda: os.remove('mkdocs.yml'))


def makedirs(path):
  """
  Create the directory *path* if it does not already exist.
  """

  if not os.path.isdir(path):
    os.makedirs(path)


# Also process all pages to copy files outside of the docs_dir to the gens_dir.
def process_pages(data, gens_dir):
  for key in data:
    filename = data[key]
    if isinstance(filename, str) and '<<' in filename:
      filename, source = filename.split('<<')
      filename, source = filename.rstrip(), source.lstrip()
      outfile = os.path.join(gens_dir, filename)
      makedirs(os.path.dirname(outfile))
      shutil.copyfile(source, outfile)
      data[key] = filename
    elif isinstance(filename, dict):
      process_pages(filename, gens_dir)
    elif isinstance(filename, list):
      [process_pages(x, gens_dir) for x in filename]


def copy_source_files(config, pages_required=True):
  """
  Copies `docs_dir` folder and its content to the `gens_dir` defined in the
  *config*. It also takes the MkDocs `pages` configuration into account
  and converts the special `<< INFILE` syntax by copying them to the
  `gens_dir` as well.
  """

  for path in config['additional_search_paths']:
    path = os.path.abspath(path)
    sys.path.append(path)

  # Copy all template files from the source directory into our
  # generated files directory.
  log('Started copying source files...')
  for root, dirs, files in os.walk(config['docs_dir']):
    rel_root = os.path.relpath(root, config['docs_dir'])
    for fname in files:
      dest_fname = os.path.join(
          config['gens_dir'], config['docs_dir'], rel_root, fname
        )
      makedirs(os.path.dirname(dest_fname))
      shutil.copyfile(os.path.join(root, fname), dest_fname)

  if 'pages' not in config:
    if pages_required:
      raise RuntimeError('pydocmd.yml does not have defined pages!')

    return

  for page in config['pages']:
    process_pages(page, config['gens_dir'])


def new_project():
  with open('pydocmd.yml', 'w') as fp:
    fp.writelines((
        'site_name: Welcome to pydoc-markdown\n',
        'generate:\n',
        'pages:\n',
        '- Home: index.md << ../README.md\n'
      ))


def log(*args, **kwargs):
  kwargs.setdefault('file', sys.stderr)
  print(*args, **kwargs)


def main():
  args = parser.parse_args()
  if args.command == 'new':
    new_project()
    return
  if args.command == 'simple' and not args.subargs:
    parser.error('need at least one argument')

  config = read_config() if args.command != 'simple' else default_config({})

  # Parse options.
  if args.command in ('generate', 'simple'):
    modspecs = []
    it = iter(args.subargs)
    while True:
      try: value = next(it)
      except StopIteration: break
      if value == '-c':
        try: value = next(it)
        except StopIteration: parser.error('missing value to option -c')
        key, value = value.partition('=')[::2]
        if value.startswith('['):
          if not value.endswith(']'):
            parser.error('invalid option value: {!r}'.format(value))
            value = value[1:-1].split(',')
        config[key] = value
      else:
        modspecs.append(value)
    args.subargs = modspecs

  loader = import_object(config['loader'])(config)
  preproc = import_object(config['preprocessor'])(config)

  if args.command != 'simple':
    mkdocs_exist = os.path.isfile('mkdocs.yml')
    copy_source_files(config, pages_required=not mkdocs_exist)

    if not mkdocs_exist:
      log('Generating temporary MkDocs config...')
      write_temp_mkdocs_config(config)

  # Build the index and document structure first, we load the actual
  # docstrings at a later point.
  log('Building index...')
  index = Index()

  def add_sections(doc, object_names, depth=1):
    if isinstance(object_names, list):
      [add_sections(doc, x, depth) for x in object_names]
    elif isinstance(object_names, dict):
      for key, subsections in object_names.items():
        add_sections(doc, key, depth)
        add_sections(doc, subsections, depth + 1)
    elif isinstance(object_names, str):
      # Check how many levels of recursion we should be going.
      expand_depth = len(object_names)
      object_names = object_names.rstrip('+')
      expand_depth -= len(object_names)

      def create_sections(name, level):
        if level > expand_depth:
          return
        index.new_section(
            doc, 
            name, 
            depth=depth + level, 
            header_type=config.get('headers', 'html'))
        sort_order = config.get('sort')
        if sort_order not in ('line', 'name'):
          sort_order = 'line'
        need_docstrings = 'docstring' in config.get('filter', ['docstring'])
        for sub in dir_object(name, sort_order, need_docstrings):
          sub = name + '.' + sub
          sec = create_sections(sub, level + 1)

      create_sections(object_names, 0)
    else:
      raise RuntimeError(object_names)

  # Make sure that we can find modules from the current working directory,
  # and have them take precedence over installed modules.
  sys.path.insert(0, '.')

  if args.command == 'simple':
    # In simple mode, we generate a single document from the import
    # names specified on the command-line.
    doc = index.new_document('main.md')
    add_sections(doc, args.subargs)
  else:
    for pages in config.get('generate') or []:
      for fname, object_names in pages.items():
        doc = index.new_document(fname)
        add_sections(doc, object_names)

  preproc.link_lookup = {}
  for file, doc in index.documents.items():
    for section in doc.sections:
      preproc.link_lookup[section.identifier] = file
  # Load the docstrings and fill the sections.
  log('Started generating documentation...')
  for doc in index.documents.values():
    for section in filter(lambda s: s.identifier, doc.sections):
      loader.load_section(section)
      preproc.preprocess_section(section)

  if args.command == 'simple':
    for section in doc.sections:
      section.render(sys.stdout)
    return 0

  # Write out all the generated documents.
  for fname, doc in index.documents.items():
    fname = os.path.join(config['gens_dir'], fname)
    makedirs(os.path.dirname(fname))
    with open(fname, 'w') as fp:
      for section in doc.sections:
        section.render(fp)

  if args.command == 'generate':
    return 0

  log("Running 'mkdocs {}'".format(args.command))
  sys.stdout.flush()

  args = ['mkdocs', args.command] + args.subargs
  try:
    return subprocess.call(args)
  except KeyboardInterrupt:
    return signal.SIGINT


if __name__ == '__main__':
  main()
