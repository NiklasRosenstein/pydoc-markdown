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
Pydoc-Markdown is a renderer for Python API documentation in Markdown format.

With no arguments it will load the default configuration file. If the
*config* argument is specified, it must be the name of a configuration file
or a YAML formatted object for the configuration.
"""

import logging
import os
import sys
import typing as t
import webbrowser

import click
import yaml
from databind.core import ConcreteType, dataclass_to_schema
from docspec import dump_module

from pydoc_markdown import __version__, PydocMarkdown, static
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Server
from pydoc_markdown.util.watchdog import watch_paths

config_filenames = [
  'pydoc-markdown.yml',
  'pydoc-markdown.yaml',
  'pyproject.toml'
]
default_config_notice = (
  'Using this option will disable loading the default configuration file.')
logger = logging.getLogger(__name__)


class RenderSession:
  """
  Helper class to load the Pydoc-markdown configuration from a file, apply
  overrides and invoke the renderer.
  """

  def __init__(self,
      config: t.Union[None, dict, str],  #: Configuration object or file
      render_toc: bool = None,  #: Override the "render_toc" option in the MarkdownRenderer
      search_path: t.List[str] = None,  #: Override the search path in the Python loader
      modules: t.List[str] = None,  #: Override the modules in the Python loader
      packages: t.List[str] = None,  #: Override the packages in the Python loader
      py2: bool = None,  #: Override Python2 compatibility in the Python loader
      ) -> None:
    self.config = config
    self.render_toc = render_toc
    self.search_path = search_path
    self.modules = modules
    self.packages = packages
    self.py2 = py2

  def _apply_overrides(self, config: PydocMarkdown):
    """
    Applies overrides to the configuration.
    """

    # Update configuration per command-line options.
    if self.modules or self.packages or self.search_path or self.py2 is not None:
      loader = next(
        (l for l in config.loaders if isinstance(l, PythonLoader)), None)
      if not loader:
        error('no python loader found')
      if self.modules:
        loader.modules = self.modules
      if self.packages:
        loader.packages = self.packages
      if self.search_path:
        loader.search_path = self.search_path
      if self.py2 is not None:
        loader.print_function = not self.py2

    if self.render_toc is not None:
      # Find the #MarkdownRenderer field for this renderer.
      schema = dataclass_to_schema(type(config.renderer))
      for field in schema.fields.values():
        if field.type == ConcreteType(MarkdownRenderer):
          markdown: MarkdownRenderer = getattr(config.renderer, field.name)
          break
      else:
        if isinstance(config.renderer, MarkdownRenderer):
          markdown = config.renderer
        else:
          error('renderer {!r} does not expose a MarkdownRenderer'
                .format(type(config.renderer).__name__))
      markdown.render_toc = self.render_toc

  def load(self) -> PydocMarkdown:
    """
    Loads the configuration and applies the overrides.
    """

    config = PydocMarkdown()
    if self.config:
      config.load_config(self.config)
    self._apply_overrides(config)

    if isinstance(self.config, str):
      config.init(Context(directory=os.path.dirname(os.path.abspath(self.config))))

    if config.unknown_fields:
      logger.warning('Unknown configuration options: %s', ', '.join(config.unknown_fields))

    return config

  def render(self, config: PydocMarkdown) -> t.List[str]:
    """
    Kicks off the rendering process and returns a list of files to watch.
    """

    modules = config.load_modules()
    config.process(modules)
    config.render(modules)

    watch_files = set(m.location.filename for m in modules)
    if isinstance(self.config, str):
      watch_files.add(self.config)

    return list(watch_files)

  def build(self, config: PydocMarkdown, site_dir: str) -> None:
    config.build(site_dir)

  def run_server(self, config: PydocMarkdown, open_browser: bool = False):
    """
    Watches files for changes and (re-) starts a server process that
    serves an HTML page from the renderer output on the fly.
    """

    if not isinstance(config.renderer, Server):
      error('renderer {!r} cannot be used with --server'
            .format(type(config.renderer).__name__))

    observer, event, process = None, None, None
    watch_files = []

    try:
      while True:
        # Initial render or re-render if a file changed.
        if not event or event.is_set():
          if event:
            config = self.load()
          logger.info('Rendering.')
          watch_files = self.render(config)
          if observer:
            observer.stop()
          observer, event = watch_paths(watch_files)
          if process:
            process = config.renderer.reload_server(process)

        # If the process doesn't exist, start it.
        if process is None:
          logger.info('Starting MkDocs serve.')
          process = config.renderer.start_server()
          if open_browser:
            open_browser = False
            webbrowser.open(config.renderer.get_server_url())

        event.wait(0.5)
    finally:
      if observer:
        observer.stop()
      if process:
        process.terminate()


def error(*args) -> t.NoReturn:
  print('error:', *args, file=sys.stderr)
  sys.exit(1)


@click.command(help=__doc__)
@click.argument('config', required=False)
@click.version_option(__version__)
@click.option('--bootstrap', type=click.Choice(['base', 'mkdocs', 'hugo', 'readthedocs', 'docusaurus']),
  help='Create a Pydoc-Markdown configuration file in the current working directory.')
@click.option('--verbose', '-v', count=True, help='Increase log verbosity.')
@click.option('--quiet', '-q', count=True, help='Decrease the log verbosity.')
@click.option('--module', '-m', 'modules', metavar='MODULE', multiple=True,
  help='The module to parse and generated API documentation for. Can be '
       'specified multiple times. ' + default_config_notice)
@click.option('--package', '-p', 'packages', metavar='PACKAGE', multiple=True,
  help='The package to parse and generated API documentation for including '
       'all sub-packages and -modules. Can be specified multiple times. '
       + default_config_notice)
@click.option('--search-path', '-I', metavar='PATH', multiple=True,
  help='A directory to use in the search for Python modules. Can be '
       'specified multiple times. ' + default_config_notice)
@click.option('--py2/--py3', 'py2', default=None,
  help='Switch between parsing Python 2 and Python 3 code. The default '
       'is Python 3. Using --py2 will enable parsing code that uses the '
       '"print" statement. This is equivalent of setting the print_function '
       'option of the "python" loader to False. ' + default_config_notice)
@click.option('--render-toc/--no-render-toc', default=None,
  help='Enable/disable the rendering of the TOC in the "markdown" renderer.')
@click.option('--server', '-s', is_flag=True,
  help='Watch for file changes and re-render if needed and start the server '
       'for the configured renderer. This doesn\'t work for all renderers.')
@click.option('--open', '-o', 'open_browser', is_flag=True,
  help='Open the browser after starting the server with -s,--server.')
@click.option('--dump', is_flag=True,
  help='Dump the loaded modules in Docspec JSON format to stdout, after the processors.')
@click.option('--with-processors/--without-processors', default=None,
  help='Enable/disable processors. Only with --dump.')
@click.option('--build', is_flag=True,
  help='Invoke a build after the Markdown files are produced. Note that some renderers may '
       'not support this option (e.g. the "markdown" renderer).')
@click.option('--site-dir', help='Set the output directory when using --build.')
def cli(
    config,
    bootstrap,
    verbose,
    quiet,
    modules,
    packages,
    search_path,
    render_toc,
    py2,
    server,
    open_browser,
    dump,
    with_processors,
    build,
    site_dir):
  """
  Command-line entrypoint for Pydoc-Markdown.
  """

  if with_processors is not None and not dump:
    error('--with-processors/--without-processors can only be used with --dump')
  if open_browser and not server:
    error('--open can only be used with --server')
  if server and build:
    error('--server and --build are incompatible options')
  if site_dir and not build:
    error('--site-dir can only be used with --build')

  if bootstrap:
    if config or modules or packages or search_path or render_toc \
        or py2 or server or open_browser or dump or with_processors is not None \
        or build or site_dir:
      error('--bootstrap must be used as a sole argument')

    if bootstrap == 'readthedocs':
      for filename in static.READTHEDOCS_FILES:
        if os.path.isfile(filename):
          error('file already exists: {!r}'.format(filename))
      for filename, content in static.READTHEDOCS_FILES.items():
        with open(filename, 'w') as fp:
          fp.write(content)
        print('created', filename)

    else:
      existing_file = next((x for x in config_filenames if os.path.isfile(x)), None)
      if existing_file:
        error('file already exists: {!r}'.format(existing_file))
      filename = config_filenames[0]
      source = {
        'base': static.DEFAULT_CONFIG,
        'mkdocs': static.DEFAULT_MKDOCS_CONFIG,
        'hugo': static.DEFAULT_HUGO_CONFIG,
        'docusaurus': static.DEFAULT_DOCUSAURUS_CONFIG,
      }
      with open(filename, 'w') as fp:
        fp.write(source[bootstrap])
      print('created', filename)

    return

  load_implicit_config = not any((modules, packages, search_path, py2 is not None))

  # Initialize logging.
  verbosity = verbose - quiet
  if verbosity >= 2:
    level = logging.DEBUG
  elif verbosity >= 1:
    level = logging.INFO
  elif verbosity >= 0:
    level = logging.WARNING
  elif verbosity >= -1:
    level = logging.ERROR
  elif verbosity >= -2:
    level = logging.CRITICAL
  else:
    level = 0
  logging.basicConfig(format='[%(levelname)s - %(name)s]: %(message)s', level=level)

  # Load the configuration.
  if config and (config.lstrip().startswith('{') or '\n' in config):
    config = yaml.safe_load(config)
  if config is None and load_implicit_config:
    try:
      config = next((x for x in config_filenames if os.path.exists(x)))
    except StopIteration:
      error('config file not found.')

  session = RenderSession(
    config=config,
    render_toc=render_toc,
    search_path=search_path,
    modules=modules,
    packages=packages,
    py2=py2)

  pydocmd = session.load()

  if dump:
    modules = pydocmd.load_modules()
    if with_processors is None or with_processors is True:
      pydocmd.process(modules)
    for module in modules:
      dump_module(module, sys.stdout)
    sys.exit(0)

  if server:
    session.run_server(pydocmd, open_browser)
  else:
    session.render(pydocmd)
    if build:
      session.build(pydocmd, site_dir)


if __name__ == '__main__':
  cli()  # pylint: disable=no-value-for-parameter
