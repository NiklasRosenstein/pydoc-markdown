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

from .document import Index
from .imp import import_object
from argparse import ArgumentParser

import atexit
import collections
import os
import shutil
import signal
import subprocess
import sys
import types
import yaml

PYDOCMD_CONFIG = 'pydocmd.yml'
parser = ArgumentParser()
parser.add_argument('command', choices=['generate', 'build', 'gh-deploy', 'json', 'new', 'serve'])


def read_config():
  """
  Reads and preprocesses the pydoc-markdown configuration file.
  """

  with open(PYDOCMD_CONFIG) as fp:
    config = yaml.load(fp)
  config.setdefault('docs_dir', 'sources')
  config.setdefault('gens_dir', '_build/pydocmd')
  config.setdefault('site_dir', '_build/site')
  config.setdefault('theme', 'readthedocs')
  config.setdefault('loader', 'pydocmd.loader.PythonLoader')
  config.setdefault('preprocessor', 'pydocmd.preprocessor.Preprocessor')
  return config


def write_mkdocs_config(inconf):
  """
  Generates a configuration for MkDocs on-the-fly from the pydoc-markdown
  configuration and makes sure it gets removed when this program exists.
  """

  config = {}
  config['site_name'] = inconf['site_name']
  config['docs_dir'] = inconf['gens_dir']
  config['site_dir'] = inconf['site_dir']
  config['theme'] = inconf['theme']
  if 'markdown_extensions' in inconf:
    config['markdown_extensions'] = inconf['markdown_extensions']
  if 'pages' in inconf:
    config['pages'] = inconf['pages']
  if 'repo_url' in inconf:
    config['repo_url'] = inconf['repo_url']

  with open('mkdocs.yml', 'w') as fp:
    yaml.dump(config, fp)

  atexit.register(lambda: os.remove('mkdocs.yml'))


def makedirs(path):
  """
  Create the directory *path* if it does not already exist.
  """

  if not os.path.isdir(path):
    os.makedirs(path)


def new_project():
  with open('pydocmd.yml', 'w') as fp:
    fp.write('site_name: Welcome to pydoc-markdown\ngenerate:\npages:\n- Home: index.md << ../README.md\n')


def main():
  args = parser.parse_args()
  if args.command == 'new':
    new_project()
    return


  config = read_config()
  loader = import_object(config['loader'])(config)
  preproc = import_object(config['preprocessor'])(config)

  # Copy all template files from the source directory into our
  # generated files directory.
  print('Started copying source files...')
  for root, dirs, files in os.walk(config['docs_dir']):
    rel_root = os.path.relpath(root, config['docs_dir'])
    for fname in filter(lambda f: f.endswith('.md'), files):
      dest_fname = os.path.join(config['gens_dir'], rel_root, fname)
      makedirs(os.path.dirname(dest_fname))
      shutil.copyfile(os.path.join(root, fname), dest_fname)

  # Also process all pages to copy files outside of the docs_dir
  # to the gens_dir.
  def process_pages(data):
    for key in data:
      filename = data[key]
      if isinstance(filename, str) and '<<' in filename:
        filename, source = filename.split('<<')
        filename, source = filename.rstrip(), source.lstrip()
        outfile = os.path.join(config['gens_dir'], filename)
        makedirs(os.path.dirname(outfile))
        shutil.copyfile(source, outfile)
        data[key] = filename
      elif isinstance(filename, dict):
        process_pages(filename)
      elif isinstance(filename, list):
        [process_pages(x) for x in filename]
  for page in config['pages']:
    process_pages(page)

  # Generate MkDocs configuration if it doesn't exist.
  if not os.path.isfile('mkdocs.yml'):
    print('Generating temporary MkDocs config...')
    write_mkdocs_config(config)

  # Build the index and document structure first, we load the actual
  # docstrings at a later point.
  print('Building index...')
  index = Index()
  def add_sections(doc, object_names, depth=1):
    if isinstance(object_names, list):
      [add_sections(doc, x, depth) for x in object_names]
    elif isinstance(object_names, dict):
      for key, subsections in object_names.items():
        add_sections(doc, key, depth)
        add_sections(doc, subsections, depth + 1)
    elif isinstance(object_names, str):
      index.new_section(doc, object_names, depth=depth)
    else: raise RuntimeError(object_names)
  for pages in config.get('generate') or []:
    for fname, object_names in pages.items():
      doc = index.new_document(fname)
      add_sections(doc, object_names)

  # Load the docstrings and fill the sections.
  print('Started generating documentation...')
  for doc in index.documents.values():
    for section in filter(lambda s: s.identifier, doc.sections):
      sub_object_names = loader.load_section(section)
      # Extract sub sections
      if sub_object_names:
        add_sections(doc, sub_object_names)
    # Load added sections
    for section in filter(lambda s: s.identifier, doc.sections):
      if not section.title:
        loader.load_section(section)

    for section in filter(lambda s: s.identifier, doc.sections):
      preproc.preprocess_section(section)

  # Write out all the generated documents.
  for fname, doc in index.documents.items():
    fname = os.path.join(config['gens_dir'], fname)
    makedirs(os.path.dirname(fname))
    with open(fname, 'w') as fp:
      for section in doc.sections:
        section.render(fp)

  if args.command == 'generate':
    return 0

  print("Running 'mkdocs {}'".format(args.command))
  sys.stdout.flush()
  try:
    return os.system('mkdocs {}'.format(args.command))
  except KeyboardInterrupt:
    return signal.SIGINT
