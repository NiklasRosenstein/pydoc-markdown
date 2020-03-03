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

from nr.databind.core import Field, Struct, forward_decl
from nr.interface import implements, override
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.reflection import Object, ModuleGraph
from typing import Iterable, List, Tuple
import copy
import fnmatch
import logging
import os
import re
import shutil
import subprocess
import yaml

logger = logging.getLogger(__name__)
Page = forward_decl()


class CustomizedMarkdownRenderer(MarkdownRenderer):
  """ We override some defaults in this subclass. """

  render_toc = Field(bool, default=False)


@forward_decl(Page)  # pylint: disable=function-redefined
class Page(Struct):
  """ Desribes a page that is rendered by the #MkdocsRenderer. """

  name = Field(str, default=None)
  title = Field(str)
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

  #: The pages to render into the output directory.
  pages = Field([Page])

  #: Markdown renderer settings.
  markdown = Field(CustomizedMarkdownRenderer, default=CustomizedMarkdownRenderer)

  #: The name of the site. This will be carried into the `site_name` key
  #: of the #mkdocs_config.
  site_name = Field(str, default='My Project')

  #: Arbitrary configuration values that will be rendered to an
  #: `mkdocs.yml` file.
  mkdocs_config = Field(dict, default=dict)

  def organize_modules(self, graph) -> Iterable[Tuple[Page, List[Object]]]:
    """ Organizes the objects in the *graph* in pairs with the pages that
    are supposed to contain them (per the "contents" filter). """

    def _match(page, node):
      if not page.contents:
        return False
      path = node.path()
      return any(fnmatch.fnmatch(path, x) for x in page.contents or ())

    def _visit(page):
      def _update_nodes(x):
        x.visible = _match(page, x)
      clone = copy.deepcopy(graph)
      clone.visit(_update_nodes)
      yield page, clone.modules
      for sub_page in page.children:
        yield from _visit(sub_page)

    for page in self.pages:
      yield from _visit(page)

  def mkdocs_serve(self):
    return subprocess.Popen(['mkdocs', 'serve'], cwd=self.output_directory)

  # Renderer

  @override
  def render(self, graph):
    docs_dir = os.path.join(self.output_directory, 'docs')
    for page, items in self.organize_modules(graph):
      filename = os.path.join(docs_dir, page.get_name() + '.md')
      os.makedirs(os.path.dirname(filename), exist_ok=True)
      if page.source:
        logger.info('Writing "%s" (source: "%s")', filename, page.source)
        shutil.copyfile(page.source, filename)
      else:
        logger.info('Rendering "%s"', filename)
        self.markdown.filename = filename
        self.markdown.render(ModuleGraph(items))

    config = copy.deepcopy(self.mkdocs_config)
    config['site_name'] = self.site_name
    config['docs_dir'] = 'docs'

    filename = os.path.join(self.output_directory, 'mkdocs.yml')
    logger.info('Rendering "%s"', filename)
    with open(filename, 'w') as fp:
      yaml.dump(config, fp)

  @override
  def get_resolver(self, _graph):
    return None  # TODO
