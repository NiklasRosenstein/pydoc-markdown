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

from nr.databind.core import Field, ProxyType, Remainder, Struct
from nr.interface import implements, override
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Renderer, Resolver, Server
from pydoc_markdown.reflection import ModuleGraph
from pydoc_markdown.util.pages import Page
from urllib.parse import urlparse, urljoin
from typing import Optional, TextIO
import logging
import os
import posixpath
import shutil
import subprocess
import toml
import yaml

logger = logging.getLogger(__name__)
HugoPage = ProxyType()


@HugoPage.implementation
class HugoPage(Page):
  preamble = Field(dict, default=dict)
  children = Field([HugoPage], default=list)


class HugoThemePath(Struct):
  path = Field(str)

  @property
  def name(self):
    return os.path.basename(self.path)

  def install(self, themes_dir: str):
    # TODO (@NiklasRosenstein): Support Windows (which does not support symlinking).
    dst = os.path.join(self.name)
    if not os.path.lexists(dst):
      os.symlink(self.path, dst)


class HugoThemeGitUrl(Struct):
  clone_url = Field(str)
  postinstall = Field([str], default=list)

  @property
  def name(self):
    return posixpath.basename(self.clone_url).rstrip('.git').lstrip('hugo-')

  def install(self, theme_dir: str):
    dst = os.path.join(theme_dir, self.name)
    if not os.path.isdir(dst):
      command = ['git', 'clone', self.clone_url, dst, '--depth', '1',
                 '--recursive', '--shallow-submodules']
      subprocess.check_call(command)
      for command in self.postinstall:
        subprocess.check_call(command, shell=True, cwd=dst)


class HugoConfig(Struct):
  baseURL = Field(str)
  languageCode = Field(str, default='en-us')
  title = Field(str)
  theme = Field((str, HugoThemePath, HugoThemeGitUrl))
  additional_options = Field(dict, Remainder())  #: Filled with the remaining options.

  def to_toml(self, fp: TextIO) -> None:
    data = self.additional_options.copy()
    for field in self.__fields__:
      if field in ('additional_options', 'theme'):
        continue
      data[field] = getattr(self, field)
    if isinstance(self.theme, str):
      data['theme'] = self.theme
    elif isinstance(self.theme, (HugoThemePath, HugoThemeGitUrl)):
      data['theme'] = self.theme.name
    else: assert False
    fp.write(toml.dumps(data))


@implements(Renderer, Server)
class HugoRenderer(Struct):
  #: The directory where all generated files are placed.
  #:
  #: Default: `build/docs`
  build_directory = Field(str, default='build/docs')

  #: The directory _inside_ the build directory where the generated
  #: pages are written to.
  #
  #: Default: `content`
  content_directory = Field(str, default='content')

  #: Clean up generated directories before rendering. Defaults to True.
  clean_render = Field(bool, default=True)

  #: The pages to render.
  pages = Field(HugoPage.collection_type())

  #: Markdown render configuration.
  markdown = Field(MarkdownRenderer, default=Field.DEFAULT_CONSTRUCT)

  #: Hugo config.toml as YAML.
  config = Field(HugoConfig)

  def _render_page(self, graph: ModuleGraph, page: HugoPage, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    preamble = {'title': page.title}
    preamble.update(page.preamble)

    with open(filename, 'w') as fp:
      fp.write('---\n')
      fp.write(yaml.safe_dump(preamble))
      fp.write('---\n\n')

      if page.source:
        with open(page.source) as src:
          shutil.copyfileobj(src, fp)
      else:
        self.markdown.fp = fp
        self.markdown.render(graph)
        self.markdown.fp = None

  # Renderer

  @override
  def render(self, graph: ModuleGraph) -> None:
    content_dir = os.path.join(self.build_directory, self.content_directory)

    if self.clean_render and os.path.isdir(content_dir):
      logger.info('Deleting directory "%s".', content_dir)
      shutil.rmtree(content_dir)

    # Render the pages.
    for item in self.pages.iter_hierarchy():
      if item.page.name == 'index':
        item.page.name = '_index'
      filename = item.filename(content_dir, '.md', index_name='_index')
      self._render_page(item.page.filtered_graph(graph), item.page, filename)

    # Render the config file.
    if isinstance(self.config.theme, (HugoThemePath, HugoThemeGitUrl)):
      self.config.theme.install(os.path.join(self.build_directory, 'themes'))
    with open(os.path.join(self.build_directory, 'config.toml'), 'w') as fp:
      self.config.to_toml(fp)

  @override
  def get_resolver(self, graph: ModuleGraph) -> Optional[Resolver]:
    # TODO (@NiklasRosenstein): The resolver returned by the Markdown
    #   renderer does not implement linking across multiple pages.
    return self.markdown.get_resolver(graph)

  # Server

  @override
  def get_server_url(self) -> str:
    urlinfo = urlparse(self.config.baseURL)
    return urljoin('http://localhost:1313/', urlinfo.path)

  @override
  def start_server(self) -> subprocess.Popen:
    return subprocess.Popen(['hugo', 'server'], cwd=self.build_directory)
