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

from nr.databind.core import Field, Remainder, Struct
from nr.interface import implements, override
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Renderer, Resolver, Server
from pydoc_markdown.reflection import ModuleGraph
from pydoc_markdown.util.pages import Page, Pages
from typing import Optional, TextIO
import logging
import os
import shutil
import subprocess
import toml
import yaml

logger = logging.getLogger(__name__)


class HugoThemePath(Struct):
  path = Field(str)


class HugoThemeGitUrl(Struct):
  clone_url = Field(str)


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
      # TODO (@NiklasRosenstein): Handle HugoThemePath and HugoThemeGitUrl
      raise NotImplementedError(type(self.theme).__name__)
    else: assert False
    fp.write(toml.dumps(data))


@implements(Renderer, Server)
class HugoRenderer(Struct):
  #: Output directory for the generated files. Defaults to build/docs.
  output_directory = Field(str, default='build/docs')

  #: Clean up generated directories before rendering. Defaults to True.
  clean_render = Field(bool, default=True)

  #: The pages to render.
  pages = Field(Pages)

  #: Markdown render configuration.
  markdown = Field(MarkdownRenderer, default=Field.DEFAULT_CONSTRUCT)

  #: Hugo config.toml as YAML.
  config = Field(HugoConfig)

  def _render_page(self, graph: ModuleGraph, page: Page, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    preamble = {'title': page.title}

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
    content_dir = os.path.join(self.output_directory, 'content')

    if self.clean_render and os.path.isdir(content_dir):
      logger.info('Deleting directory "%s".', content_dir)
      shutil.rmtree(content_dir)

    # Render the pages.
    for item in self.pages.iter_hierarchy():
      filename = item.filename(content_dir, '.md')
      if not filename:
        continue
      self._render_page(item.page.filtered_graph(graph), item.page, filename)

    # Render the config file.
    # TODO (@NiklasRosenstein): Handle the case where the config specifies
    #   a #HugoThemePath or #HugoThemeGitUrl.
    with open(os.path.join(self.output_directory, 'config.toml'), 'w') as fp:
      self.config.to_toml(fp)

  @override
  def get_resolver(self, graph: ModuleGraph) -> Optional[Resolver]:
    # TODO (@NiklasRosenstein): The resolver returned by the Markdown
    #   renderer does not implement linking across multiple pages.
    return self.markdown.get_resolver(graph)

  # Server

  @override
  def get_server_url(self) -> str:
    return 'http://localhost:1313/'

  @override
  def start_server(self) -> subprocess.Popen:
    return subprocess.Popen(['hugo', 'server'], cwd=self.output_directory)
