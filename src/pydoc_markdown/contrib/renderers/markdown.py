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
Implements a renderer that produces Markdown output.
"""

import io
import sys

from nr.types.struct import Field, Struct
from nr.types.interface import implements
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.reflection import *


@implements(Renderer)
class MarkdownRenderer(Struct):
  filename = Field(str, default=None)
  encoding = Field(str, default='utf8')
  html_headings = Field(bool, default=False)
  code_headings = Field(bool, default=True)
  code_lang = Field(bool, default=True)
  descriptive_class_title = Field(bool, default=True)
  add_method_class_prefix = Field(bool, default=True)
  add_full_prefix = Field(bool, default=False)
  sub_prefix = Field(bool, default=False)
  signature_code_block = Field(bool, default=True)
  signature_in_header = Field(bool, default=False)
  signature_with_def = Field(bool, default=True)
  signature_class_prefix = Field(bool, default=False)
  signature_expression_maxlength = Field(int, default=100)
  render_toc = Field(bool, default=True)
  render_toc_title = Field(str, default='Table of Contents')
  toc_maxdepth = Field(int, default=2)

  def _render_toc(self, fp, level, obj):
    if level > self.toc_maxdepth:
      return
    object_id = self._generate_object_id(obj)
    fp.write('  ' * level + '* [{}](#{})\n'.format(self._escape(obj.name), object_id))
    for child in obj.members.values():
      self._render_toc(fp, level + 1, child)

  def _render_object(self, fp, level, obj):
    if self.html_headings:
      object_id = self._generate_object_id(obj)
      heading_template = '<h{0} id="{1}">{{title}}</h{0}>'.format(level, object_id)
    else:
      heading_template = level * '#' + ' {title}'
    fp.write(heading_template.format(title=self._get_title(obj)))
    fp.write('\n\n')
    if self.signature_code_block and (obj.is_class() or obj.is_function()):
      if obj.is_class():
        func = obj.members.get('__init__')
        if func and not func.is_function():
          func = None
      else:
        func = obj
      if func:
        fp.write('```{}\n'.format('python' if self.code_lang else ''))
        for dec in func.decorators:
          fp.write('@{}{}\n'.format(dec.name, dec.args or ''))
        if func.is_async:
          fp.write('async ')
        if self.signature_with_def:
          fp.write('def ')
        if self.signature_class_prefix and (
            func.is_function() and func.parent and func.parent.is_class()):
          fp.write(func.parent.name + '.')
        fp.write(func.signature)
        if func.return_:
          fp.write(' -> {}'.format(func.return_))
        fp.write('\n```\n\n')
    if self.signature_code_block and obj.is_data():
      fp.write('```{}\n'.format('python' if self.code_lang else ''))
      expr = str(obj.expr)
      if len(expr) > self.signature_expression_maxlength:
        expr = expr[:self.signature_expression_maxlength] + ' ...'
      fp.write(obj.name + ' = ' + expr)
      fp.write('\n```\n\n')
    if obj.docstring:
      fp.write(obj.docstring)
      fp.write('\n')
    fp.write('\n')

  def _render_recursive(self, fp, level, obj):
    self._render_object(fp, level, obj)
    for member in obj.members.values():
      self._render_recursive(fp, level+1, member)

  def _render(self, graph, fp):
    if self.render_toc:
      if self.render_toc_title:
        fp.write('# {}\n\n'.format(self.render_toc_title))
      for m in graph.modules:
        self._render_toc(fp, 1, m)
      fp.write('\n')
    for m in graph.modules:
      self._render_recursive(fp, 1, m)

  def _get_title(self, obj):
    title = obj.name
    if self.add_method_class_prefix and obj.is_method():
      title = obj.parent.name + '.' + title
    elif self.add_full_prefix and not obj.is_method():
      title = obj.path()

    if obj.is_function():
      if self.signature_in_header:
        title += '(' + obj.signature_args + ')'
      else:
        title += '()'

    if self.code_headings:
      if self.html_headings or self.sub_prefix:
        if self.sub_prefix and '.' in title:
          prefix, title = title.rpartition('.')[::2]
          title = '<sub>{}.</sub>{}'.format(prefix, title)
        title = '<code>{}</code>'.format(title)
      else:
        title ='`{}`'.format(title)
    else:
      title = obj.name
    if isinstance(obj, Class) and self.descriptive_class_title:
      title += ' Objects'
    return title

  def _generate_object_id(self, obj):
    parts = []
    while obj:
      parts.append(obj.name)
      obj = obj.parent
    return '.'.join(reversed(parts))

  def _escape(self, s):
    return s.replace('_', '\\_').replace('*', '\\*')

  # Renderer

  def render(self, graph):
    if self.filename is None:
      self._render(graph, sys.stdout)
    else:
      with io.open(self.filename, 'w', encoding=self.encoding) as fp:
        self._render(graph, fp)
