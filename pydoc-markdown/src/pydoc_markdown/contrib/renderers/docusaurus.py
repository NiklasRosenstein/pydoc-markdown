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

from docspec_python import format_arglist
from nr.databind.core import Field, Struct, Validator
from nr.interface import implements, override
from pathlib import Path
from pydoc_markdown.interfaces import Context, Renderer, Resolver, SourceLinker
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from typing import Iterable, List, Optional, TextIO
import docspec
import html
import io
import sys


@implements(Renderer)
class DocusaurusRenderer(MarkdownRenderer):
  """
  Produces Markdown files. This renderer is often used by other renderers, such as
  #MkdocsRenderer and #HugoRenderer. It provides a wide variety of options to customize
  the generated Markdown files.

  ### Options
  """

  #: If enabled, inserts anchors before Markdown headers to ensure that
  #: links to the header work. This is disabled by default because Docusaurus
  #: supports this automatically.
  insert_header_anchors = Field(bool, default=False)

  #: The path where to write the multiple docs files,
  #: when `render_multiple_files` is True. Defaults to the
  #: current working directory.
  output_path = Field(str, default='.')

  #: Skip documenting modules if empty. Defaults to True.
  skip_empty_modules = Field(bool, default=True)

  #: Escape html in docstring. Default to True.
  escape_html_in_docstring = Field(bool, default=True)

  def _render_header(self, fp, level, obj):
    # TODO: render docusaurus header
    return super(DocusaurusRenderer, self)._render_header(fp, level, obj)

  def _render_recursive(self, fp, level, obj):
    members = getattr(obj, 'members', [])
    if self.skip_empty_modules and isinstance(obj, docspec.Module) and not members:
      return

    return super(DocusaurusRenderer, self)._render_recursive(fp, level, obj)

  @override
  def render(self, modules: List[docspec.Module]) -> None:
    for module in modules:
      module_parts = module.name.split(".")
      filepath = Path(self.output_path)
      for module_part in module_parts[:-1]:
        filepath = filepath / module_part

      filepath.mkdir(parents=True, exist_ok=True)
      filepath = filepath / f"{module_parts[-1]}.md"
      with filepath.open('w', encoding=self.encoding) as fp:
        self._render_modules([module], fp)
      if self.skip_empty_modules and not filepath.read_text():
        filepath.unlink()
