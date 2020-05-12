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

""" Implements the `mkdocs` renderer. It uses the `markdown` renderer to
produce an MkDocs-compatible folder structure. """

from nr.databind.core import Field, Struct, ProxyType
from nr.interface import implements, override
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.reflection import Object, ModuleGraph
from typing import Dict, Iterable, List, Tuple
import copy
import fnmatch
import logging
import os
import re
import shutil
import subprocess
import yaml

logger = logging.getLogger(__name__)
Page = ProxyType()


class CustomizedMarkdownRenderer(MarkdownRenderer):
  """ We override some defaults in this subclass. """

  render_toc = Field(bool, default=False)


@Page.implementation  # pylint: disable=function-redefined
class Page(Struct):
  """ Desribes a page that is rendered by the #MkdocsRenderer. """

  name = Field(str, default=None)
  title = Field(str)
  href = Field(str, default=None)
  source = Field(str, default=None)
  contents = Field([str], default=None)
  children = Field([Page], default=list)

  def get_name(self):
    if self.name:
      return self.name
    return re.sub(r'\s+', '-', self.title.lower())


@implements(Renderer)
class MkdocsRenderer(Struct):
  #: The output directory for the generated Markdown files. Defaults to
  #: `build/docs`.
  output_directory = Field(str, default='build/docs')

  #: Remove the `docs` directory in the #output_directory before rendering.
  clean_docs_directory_on_render = Field(bool, default=True)

  #: The pages to render into the output directory.
  pages = Field([Page])

  #: Markdown renderer settings.
  markdown = Field(CustomizedMarkdownRenderer, default=CustomizedMarkdownRenderer)

  #: The name of the site. This will be carried into the `site_name` key
  #: of the #mkdocs_config.
  site_name = Field(str, default=None)

  #: Arbitrary configuration values that will be rendered to an
  #: `mkdocs.yml` file.
  mkdocs_config = Field(dict, default=dict)

  @property
  def docs_dir(self) -> str:
    return os.path.join(self.output_directory, 'docs')

  def organize_modules(self, graph) -> Iterable[Tuple[List[str], Page, List[Object]]]:
    """ Organizes the objects in the *graph* in pairs with the pages that
    are supposed to contain them (per the "contents" filter). """

    def _match(page, node):
      if not page.contents:
        return False
      path = node.path()
      return any(fnmatch.fnmatch(path, x) for x in page.contents or ())

    def _visit(page, path):
      def _update_nodes(x):
        x.visible = x.visible and _match(page, x)
        # Make sure all parents are visible as well.
        while x and x.visible:
          x = x.parent
          if x:
            x.visible = True
      clone = copy.deepcopy(graph)
      clone.visit(_update_nodes)
      yield path, page, clone.modules
      path = path + [page.get_name()]
      for sub_page in page.children:
        yield from _visit(sub_page, path)

    for page in self.pages:
      yield from _visit(page, [])

  def mkdocs_serve(self):
    return subprocess.Popen(['mkdocs', 'serve'], cwd=self.output_directory)

  def generate_mkdocs_nav(self, page_to_filename: Dict[Page, str]) -> Dict:
    def _generate(pages):
      result = []
      for page in pages:
        if page.children:
          result.append({page.title: _generate(page.children)})
        elif page.href:
          result.append({page.title: page.href})
        else:
          filename = os.path.relpath(page_to_filename[id(page)], self.docs_dir)
          result.append({page.title: filename})
      return result
    return _generate(self.pages)

  # Renderer

  @override
  def render(self, graph):
    if self.clean_docs_directory_on_render and os.path.isdir(self.docs_dir):
      logger.info('Cleaning directory "%s"', self.docs_dir)
      shutil.rmtree(self.docs_dir)

    page_to_filename = {}

    for path, page, items in self.organize_modules(graph):
      # Construct the filename for the generated Markdown page.
      path = path + [page.get_name()]
      if page.children:
        if not page.contents and not page.source:
          continue
        path.append('index')
      filename = os.path.join(self.docs_dir, *path) + '.md'
      page_to_filename[id(page)] = filename

      # Render the page or copy from the specified source file.
      os.makedirs(os.path.dirname(filename), exist_ok=True)
      if page.source:
        logger.info('Writing "%s" (source: "%s")', filename, page.source)
        shutil.copyfile(page.source, filename)
      else:
        logger.info('Rendering "%s"', filename)
        self.markdown.filename = filename
        self.markdown.render(ModuleGraph(items))

    config = copy.deepcopy(self.mkdocs_config)
    if self.site_name:
      config['site_name'] = self.site_name
    if not config.get('site_name'):
      config['site_name'] = 'My Project'
    config['docs_dir'] = 'docs'
    config['nav'] = self.generate_mkdocs_nav(page_to_filename)

    filename = os.path.join(self.output_directory, 'mkdocs.yml')
    logger.info('Rendering "%s"', filename)
    with open(filename, 'w') as fp:
      yaml.dump(config, fp)

  @override
  def get_resolver(self, graph):
    return self.markdown.get_resolver(graph)
