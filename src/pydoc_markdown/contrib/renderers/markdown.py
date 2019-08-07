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

from nr.types.structured import Field, Object
from nr.types.interface import implements
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.reflection import *


class MarkdownRendererConfig(Object):
  filename = Field(str, default=None)
  encoding = Field(str, default='utf8')
  html_headings = Field(bool, default=False)
  code_headings = Field(bool, default=True)
  descriptive_class_title = Field(bool, default=True)
  add_method_class_prefix = Field(bool, default=True)
  add_full_prefix = Field(bool, default=False)
  sub_prefix = Field(bool, default=False)
  signature_below_heading = Field(bool, default=True)
  signature_in_heading = Field(bool, default=False)

  # TODO(nrosenstein): render_toc option


@implements(Renderer)
class MarkdownRenderer(object):

  CONFIG_CLASS = MarkdownRendererConfig

  def render_object(self, fp, level, obj):
    if self.config.html_headings:
      heading_template = '<h{}>{{title}}</h{}>'.format(level)
    else:
      heading_template = level * '#' + ' {title}'
    fp.write(heading_template.format(title=self.get_title(obj)))
    fp.write('\n\n')
    if self.config.signature_below_heading and (obj.is_class() or obj.is_function()):
      if obj.is_class():
        func = obj.members.get('__init__')
        if func and not func.is_function():
          func = None
      else:
        func = obj
      if func:
        fp.write('```python\n')
        for dec in func.decorators:
          fp.write('@{}{}\n'.format(dec.name, dec.args or ''))
        if func.is_async:
          fp.write('async ')
        fp.write('def ')
        fp.write(func.signature)
        fp.write('\n```\n\n')
    if self.config.signature_below_heading and obj.is_data():
      fp.write('```python\n')
      fp.write(obj.name + ' = ' + str(obj.expr))
      fp.write('\n```\n\n')
    if obj.docstring:
      fp.write(obj.docstring)
      fp.write('\n')
    fp.write('\n')

  def render_recursive(self, fp, level, obj):
    self.render_object(fp, level, obj)
    for member in obj.members.values():
      self.render_recursive(fp, level+1, member)

  def get_title(self, obj):
    title = obj.name
    if self.config.add_method_class_prefix and obj.is_method():
      title = obj.parent.name + '.' + title
    elif self.config.add_full_prefix and not obj.is_method():
      title = obj.path()

    if obj.is_function():
      if self.config.signature_in_heading:
        title += '(' + obj.signature_args + ')'
      else:
        title += '()'

    if self.config.code_headings:
      if self.config.html_headings or self.config.sub_prefix:
        if self.config.sub_prefix and '.' in title:
          prefix, title = title.rpartition('.')[::2]
          title = '<sub>{}.</sub>{}'.format(prefix, title)
        title = '<code>{}</code>'.format(title)
      else:
        title ='`{}`'.format(title)
    else:
      title = obj.name
    if isinstance(obj, Class) and self.config.descriptive_class_title:
      title += ' Objects'
    return title

  # Renderer

  def render(self, config, graph):
    if self.config.filename is None:
      for m in graph.modules:
        self.render_recursive(sys.stdout, 1, m)
    else:
      with io.open(self.config.filename, 'w', encoding=self.config.encoding) as fp:
        for m in graph.modules:
          self.render_recursive(fp, 1, m)
