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

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.contrib.renderers.mkdocs import MkdocsRenderer
from pydoc_markdown.util.watchdog import watch_paths
import click
import logging
import os
import sys
import webbrowser
import yaml

logger = logging.getLogger(__name__)

config_filenames = [
  'pydoc-markdown.yml',
  'pydoc-markdown.yaml',
]

MKDOCS_DEFAULT_SERVE_URL = 'http://localhost:8000'
DEFAULT_CONFIG_NOTICE = 'Using this option will disable loading the '\
  'default configuration file.'
DEFAULT_CONFIG = '''
loaders:
  - type: python
processors:
  - type: filter
  - type: smart
  - type: crossref
renderer:
  - type: markdown
'''.lstrip()
DEFAULT_CONFIG_MKDOCS = '''
loaders:
  - type: python
processors:
  - type: filter
  - type: smart
  - type: crossref
renderer:
  type: mkdocs
  pages:
    - title: Home
      name: index
      source: README.md
    - title: API Documentation
      contents:
        - my_module.api.*
  mkdocs_config:
    theme: readthedocs
'''.lstrip()


def error(*args):
  print('error:', *args, file=sys.stderr)
  sys.exit(1)


@click.command()
@click.argument('config', required=False)
@click.option('--bootstrap',
  is_flag=True,
  help='Render the default configuration file into the current working directory and quit.')
@click.option('--bootstrap-mkdocs',
  is_flag=True,
  help='Render a template configuration file for generating MkDpcs files into the current '
       'working directory and quit.')
@click.option('--verbose', '-v',
  is_flag=True,
  help='Increase log verbosity.')
@click.option('--quiet', '-q',
  is_flag=True,
  help='Decrease the log verbosity.')
@click.option('--module', '-m', 'modules',
  metavar='MODULE',
  multiple=True,
  help='The module to parse and generated API documentation for. Can be '
       'specified multiple times. ' + DEFAULT_CONFIG_NOTICE)
@click.option('--search-path', '-I',
  metavar='PATH',
  multiple=True,
  help='A directory to use in the search for Python modules. Can be '
       'specified multiple times. ' + DEFAULT_CONFIG_NOTICE)
@click.option('--py2/--py3', 'py2',
  default=None,
  help='Switch between parsing Python 2 and Python 3 code. The default '
       'is Python 3. Using --py2 will enable parsing code that uses the '
       '"print" statement. This is equivalent of setting the print_function '
       'option of the "python" loader to False. ' + DEFAULT_CONFIG_NOTICE)
@click.option('--render-toc/--no-render-toc',
  default=None,
  help='Enable/disable the rendering of the TOC in the "markdown" renderer.')
@click.option('--watch-and-serve', '-w',
  is_flag=True,
  help='Watch for file changes and re-render if needed, and run "mkdocs '
       'serve" in the background. This option is only supported for the '
       '"mkdocs" renderer.')
@click.option('--open', '-o', 'open_browser',
  is_flag=True,
  help='Open your browser after starting "mkdocs serve". Can only be used '
       'together with the --watch-and-serve option.')
def cli(
    config,
    bootstrap,
    bootstrap_mkdocs,
    verbose,
    quiet,
    modules,
    search_path,
    render_toc,
    py2,
    watch_and_serve,
    open_browser):
  """ Pydoc-Markdown is a renderer for Python API documentation in Markdown
  format.

  With no arguments it will load the default configuration file. If the
  *config* argument is specified, it must be the name of a configuration file
  or a YAML formatted object for the configuration. """

  if bootstrap and bootstrap_mkdocs:
    error('--bootstrap and --bootstrap-mkdocs are incompatible options')
  if bootstrap or bootstrap_mkdocs:
    if config or modules or search_path or render_toc or py2 or watch_and_serve or open_browser:
      error('--bootstrap must be used as a sole argument')
    existing_file = next((x for x in config_filenames if os.path.isfile(x)), None)
    if existing_file:
      error('file already exists: {!r}'.format(existing_file))
    filename = config_filenames[0]
    with open(filename, 'w') as fp:
      if bootstrap_mkdocs:
        fp.write(DEFAULT_CONFIG_MKDOCS)
      else:
        fp.write(DEFAULT_CONFIG)
    print('created', filename)
    return

  if open_browser and not watch_and_serve:
    error('--open can only be used with --watch-and-serve')

  load_implicit_config = not any((modules, search_path, py2 is not None))

  # Initialize logging.
  if verbose is not None:
    if verbose:
      level = logging.INFO
    elif quiet:
      level = logging.ERROR
    else:
      level = logging.WARNING
    logging.basicConfig(format='%(message)s', level=level)

  # Load the configuration.
  if config and (config.lstrip().startswith('{') or '\n' in config):
    config = yaml.safe_load(config)
  if config is None and load_implicit_config:
    try:
      config = next((x for x in config_filenames if os.path.exists(x)))
    except StopIteration:
      error('config file not found.')

  def _apply_overrides(pydocmd):
    # Update configuration per command-line options.
    if modules or search_path or py2 is not None:
      loader = next(
        (l for l in pydocmd.loaders if isinstance(l, PythonLoader)), None)
      if not loader:
        error('no python loader found')
      if modules:
        loader.modules = modules
      if search_path:
        loader.search_path = search_path
      if py2 is not None:
        loader.print_function = not py2
    if render_toc is not None:
      if isinstance(pydocmd.renderer, MkdocsRenderer):
        markdown = pydocmd.renderer.markdown
      elif isinstance(pydocmd.renderer, MarkdownRenderer):
        markdown = pydocmd.renderer
      else:
        error('no markdown renderer found')
      if render_toc is not None:
        markdown.render_toc = render_toc
    if watch_and_serve:
      if not isinstance(pydocmd.renderer, MkdocsRenderer):
        error('--watch-and-serve can only be used in combination with '
              'the "mkdocs" renderer.')

  def _load_process_render():
    pydocmd = PydocMarkdown()
    if config:
      pydocmd.load_config(config)

    _apply_overrides(pydocmd)

    pydocmd.load_modules()
    pydocmd.process()
    pydocmd.render()

    watch_files = set(m.location.filename for m in pydocmd.graph.modules)
    if isinstance(config, str):
      watch_files.add(config)

    return pydocmd, watch_files

  if not watch_and_serve:
    _load_process_render()
    return

  # Watch and re-render if needed. We rely on "mkdocs serve" to also
  # be on watch duty, so we won't need to restart that process everytime.
  observer, event = None, None
  proc = None
  try:
    while True:
      if not event or event.is_set():
        logger.info('Rendering.')
        pydocmd, watch_files = _load_process_render()
        if observer:
          observer.stop()
        observer, event = watch_paths(watch_files)
      if proc is None:
        logger.info('Starting MkDocs serve.')
        proc = pydocmd.renderer.mkdocs_serve()
        if open_browser:
          webbrowser.open(MKDOCS_DEFAULT_SERVE_URL)
      event.wait(0.5)
  finally:
    if observer:
      observer.stop()
    if proc:
      proc.terminate()


if __name__ == '__main__':
  cli()  # pylint: disable=no-value-for-parameter
