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

import dataclasses
import copy
import logging
import os
import subprocess
import typing as t
import typing_extensions as te

import databind.core.annotations as A
import docspec
import yaml

from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer, Resolver, Server, Builder
from pydoc_markdown.util.pages import Page, Pages
from pydoc_markdown.util.knownfiles import KnownFiles
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class CustomizedMarkdownRenderer(MarkdownRenderer):
  """ We override some defaults in this subclass. """

  render_toc: bool = False


@dataclasses.dataclass
class MkdocsRenderer(Renderer, Server, Builder):
  """
  Produces Markdown files in a layout compatible with [MkDocs][0] and can be used with the
  Pydoc-Markdown `--server` option for a live-preview. The `--bootstrap mkdocs` option can
  be used to create a Pydoc-Markdown configuration file with the MkDocs template.

  Example configuration:

  ```yml
  renderer:
    type: mkdocs
    pages:
      - title: Home
        name: index
        source: README.md
      - title: API Documentation
        contents:
          - '*'
    mkdocs_config:
      mkdocs_config:
        site_name: My Project
        theme: readthedocs
  ```

  ### Options
  """

  #: The output directory for the generated Markdown files. Defaults to
  #: `build/docs`.
  output_directory: str = 'build/docs'

  #: Name of the content directory (inside the #output_directory). Defaults to "content".
  content_directory_name: str = 'content'

  #: Remove files generated in a previous pass by the Mkdocs renderer before rendering
  #: again. Defaults to `True`.
  clean_render: bool = True

  #: The pages to render into the output directory.
  # TODO (@NiklasRosenstein): Uh what exactly is this in new databind?
  pages: Pages[Page] = dataclasses.field(default_factory=Pages)

  #: Markdown renderer settings.
  # TODO (@NiklasRosenstein): Use fieldinfo(serialize_as)
  markdown: te.Annotated[MarkdownRenderer, A.typeinfo(deserialize_as=CustomizedMarkdownRenderer)] = \
    dataclasses.field(default_factory=CustomizedMarkdownRenderer)

  #: The name of the site. This will be carried into the `site_name` key
  #: of the #mkdocs_config.
  site_name: t.Optional[str] = None

  #: Arbitrary configuration values that will be rendered to an
  #: `mkdocs.yml` file.
  mkdocs_config: t.Optional[t.Dict[str, t.Any]] = dataclasses.field(default_factory=dict)

  #: Port for the Mkdocs server when using the `pydoc-markdown --server` option.
  #: Defaults to `8000`. Can be set with the `MKDOCS_PORT` environment variable:
  #:
  #: ```
  #: $ MKDOCS_PORT=8383 pydoc-markdown -so
  #: ```
  server_port: t.Optional[int] = None

  def __post_init__(self) -> None:
    self._context: t.Optional[Context] = None

  @property
  def content_dir(self) -> str:
    return os.path.join(self.output_directory, self.content_directory_name)

  def generate_mkdocs_nav(self, page_to_filename: Dict[Page, str]) -> Dict:
    def _generate(pages):
      result = []
      for page in pages:
        if page.children:
          result.append({page.title: _generate(page.children)})
        elif page.href:
          result.append({page.title: page.href})
        else:
          filename = os.path.relpath(page_to_filename[id(page)], self.content_dir)
          if os.name == 'nt':
            # Make generated configuration more portable across operating systems (see #129).
            filename = filename.replace('\\', '/')
          result.append({page.title: filename})
      return result
    return _generate(self.pages)

  def _get_addr(self) -> str:
    if self.server_port is None:
      port = int(os.getenv('MKDOCS_PORT', '8000'))
    else:
      port = self.server_port
    return 'localhost:{}'.format(port)

  # Renderer

  def render(self, modules: List[docspec.Module]) -> None:
    known_files = KnownFiles(self.output_directory)
    if self.clean_render:
      for file_ in known_files.load():
        try:
          os.remove(file_.name)
        except FileNotFoundError:
          pass

    page_to_filename = {}

    with known_files:
      for item in self.pages.iter_hierarchy():
        filename = item.filename(self.content_dir, '.md')
        page_to_filename[id(item.page)] = filename
        if not item.page.has_content():
          continue

        self.markdown.filename = filename
        item.page.render(filename, modules, self.markdown, context_directory=self._context.directory)
        known_files.append(filename)

      config = copy.deepcopy(self.mkdocs_config)
      if self.site_name:
        config['site_name'] = self.site_name
      if not config.get('site_name'):
        config['site_name'] = 'My Project'
      config['docs_dir'] = self.content_directory_name
      config['nav'] = self.generate_mkdocs_nav(page_to_filename)

      if self.mkdocs_config is not None:
        filename = os.path.join(self.output_directory, 'mkdocs.yml')
        logger.info('Rendering "%s"', filename)
        with known_files.open(filename, 'w') as fp:
          yaml.dump(config, fp)

  def get_resolver(self, modules: List[docspec.Module]) -> Optional[Resolver]:
    # TODO (@NiklasRosenstein): The resolver returned by the Markdown
    #   renderer does not implement linking across multiple pages.
    return self.markdown.get_resolver(modules)

  # Server

  def get_server_url(self) -> str:
    return 'http://{}'.format(self._get_addr())

  def start_server(self) -> subprocess.Popen:
    addr = self._get_addr()
    return subprocess.Popen(['mkdocs', 'serve', '-a', addr], cwd=self.output_directory)

  def reload_server(self, process: subprocess.Popen):
    # While MkDocs does support file watching and automatic reloading,
    # it appears to be a bit quirky. Let's just restart the whole process.
    process.terminate()

  # Builder

  def build(self, site_dir: str) -> None:
    command = ['mkdocs', 'build', '--clean', '--site-dir', site_dir]
    subprocess.check_call(command, cwd=self.output_directory)

  # PluginBase

  def init(self, context: Context) -> None:
    self._context = context
    self.markdown.init(context)
