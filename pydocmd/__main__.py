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

from .document import Section, Document
from .imp import import_object
from argparse import ArgumentParser

import atexit
import collections
import os
import shutil
import subprocess
import types
import yaml

PYDOCMD_CONFIG = 'pydocmd.yml'
parser = ArgumentParser()
parser.add_argument('command', choices=['build', 'gh-deploy', 'json', 'new', 'serve'])


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
  if 'pages' in inconf:
    config['pages'] = inconf['pages']

  with open('mkdocs.yml', 'w') as fp:
    yaml.dump(config, fp)
  atexit.register(lambda: os.remove('mkdocs.yml'))


def makedirs(path):
  """
  Create the directory *path* if it does not already exist.
  """

  if not os.path.isdir(path):
    os.makedirs(path)


def main():
  args = parser.parse_args()
  config = read_config()

  # Generate MkDocs configuration if it doesn't exist.
  if not os.path.isfile('mkdocs.yml'):
    write_mkdocs_config(config)

  # Copy all template files from the source directory into our
  # generated files directory.
  print('Started copying source files...')
  for root, dirs, files in os.walk(config['docs_dir']):
    for fname in filter(lambda f: f.endswith('.md'), files):
      dest_fname = os.path.join(config['gens_dir'], fname)
      makedirs(os.path.dirname(dest_fname))
      shutil.copyfile(os.path.join(root, fname), dest_fname)

  print('Building documentation index...')
  index = collections.OrderedDict()
  documents = {}
  for item in config.get('generate', []):
    for fname, object_names in item.items():
      doc = Document(fname.rstrip('.md'))
      documents[os.path.join(config['gens_dir'], fname)] = doc
      index.update({x: doc for x in object_names})

  print('Started generating documentation...')
  for name, doc in index.items():
    # TODO: Process docstrings, establish cross-links etc.
    obj = import_object(name)
    section = doc.add(name)
    name = obj.__name__
    if isinstance(obj, (types.FunctionType, types.LambdaType)):
      name += '()'
    docstring = getattr(obj, '__doc__', None) or ''
    docstring = '# {}\n'.format(name) + docstring
    section.content = docstring

  # Write out all the generated documents.
  for fname, doc in documents.items():
    makedirs(os.path.dirname(fname))
    with open(fname, 'w') as fp:
      doc.render(fp)

  print("Running 'mkdocs {}'".format(args.command))
  return subprocess.call(['mkdocs', args.command])
