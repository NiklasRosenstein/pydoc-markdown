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

from nr.databind.core import Field, Struct
from nr.interface import implements
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.reflection import Class, Module


@implements(Renderer)
class MarkdownRenderer(Struct):
  #: The name of the file to render to. If no file is specified, it will
  #: render to stdout.
  filename = Field(str, default=None)

  #: The encoding of the output file. This is ignored when rendering to
  #: stdout.
  encoding = Field(str, default='utf8')

  #: If enabled, inserts anchors before Markdown headers to ensure that
  #: links to the header work. This is enabled by default.
  insert_header_anchors = Field(bool, default=True)

  #: Generate HTML headers instead of Mearkdown headers. This is disabled
  #: by default.
  html_headers = Field(bool, default=False)

  #: Render names in headers as code (using backticks or `<code>` tags,
  #: depending on #html_headers). This is enabled by default.
  code_headers = Field(bool, default=True)

  #: Generate descriptive class titles by adding the word "Objects" after
  #: the class name. This is enabled by default.
  descriptive_class_title = Field(bool, default=True)

  #: Generate descriptivie module titles by adding the word "Module" before
  #: the module name. This is enabled by default.
  descriptive_module_title = Field(bool, default=True)

  #: Add the class name as a prefix to method names. This class name is
  #: also rendered as code if #code_headers is enabled. This is enabled
  #: by default.
  add_method_class_prefix = Field(bool, default=True)

  #: Add the full module name as a prefix to the title of the header.
  #: This is disabled by default.
  add_full_prefix = Field(bool, default=False)

  #: If #add_full_prefix is enabled, this will result in the prefix to
  #: be wrapped in a `<sub>` tag.
  sub_prefix = Field(bool, default=False)

  #: Render the definition of data members as a code block. This is disabled
  #: by default.
  data_code_block = Field(bool, default=False)

  #: Max length of expressions. If this limit is exceeded, the remaining
  #: characters will be replaced with three dots. This is set to 100 by
  #: default.
  data_expression_maxlength = Field(int, default=100)

  #: Render the class signature as a code block. This includes the "class"
  #: keyword, the class name and its bases. This is enabled by default.
  classdef_code_block = Field(bool, default=True)

  #: Render the function signature as a code block. This includes the "def"
  #: keyword, the function name and its arguments. This is enabled by
  #: default.
  signature_code_block = Field(bool, default=True)

  #: Render the function signature in the header. This is disabled by default.
  signature_in_header = Field(bool, default=False)

  #: Include the "def" keyword in the function signature. This is enabled
  #: by default.
  signature_with_def = Field(bool, default=True)

  #: Render the class name in the code block for function signature. Note
  #: that this results in invalid Python syntax to be rendered. This is
  #: disabled by default.
  signature_class_prefix = Field(bool, default=False)

  #: Add the string "python" after the backticks for code blocks. This is
  #: enabled by default.
  code_lang = Field(bool, default=True)

  #: Render a table of contents at the beginning of the file.
  render_toc = Field(bool, default=True)

  #: The title of the "Table of Contents" header.
  render_toc_title = Field(str, default='Table of Contents')

  #: The maximum depth of the table of contents. Defaults to 2.
  toc_maxdepth = Field(int, default=2)

  #: Render module headers. This is enabled by default.
  render_module_header = Field(bool, default=True)

  #: Render docstrings as blockquotes. This is disabled by default.
  docstrings_as_blockquote = Field(bool, default=False)

  def _render_toc(self, fp, level, obj):
    if level > self.toc_maxdepth:
      return
    object_id = self._generate_object_id(obj)
    fp.write('  ' * level + '* [{}](#{})\n'.format(self._escape(obj.name), object_id))
    for child in obj.members.values():
      self._render_toc(fp, level + 1, child)

  def _render_header(self, fp, level, obj):
    object_id = self._generate_object_id(obj)
    if self.insert_header_anchors and not self.html_headers:
      fp.write('<a name="{}"></a>\n'.format(object_id))
    if self.html_headers:
      header_template = '<h{0} id="{1}">{{title}}</h{0}>'.format(level, object_id)
    else:
      header_template = level * '#' + ' {title}'
    fp.write(header_template.format(title=self._get_title(obj)))
    fp.write('\n\n')

  def _render_signature_block(self, fp, func):
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

  def _render_data_block(self, fp, obj):
    fp.write('```{}\n'.format('python' if self.code_lang else ''))
    expr = str(obj.expr)
    if len(expr) > self.data_expression_maxlength:
      expr = expr[:self.data_expression_maxlength] + ' ...'
    fp.write(obj.name + ' = ' + expr)
    fp.write('\n```\n\n')

  def _render_object(self, fp, level, obj):
    if not isinstance(obj, Module) or self.render_module_header:
      self._render_header(fp, level, obj)
    if self.classdef_code_block and obj.is_class():
      bases = ', '.join(map(str, obj.bases))
      fp.write('```python\nclass {}({})\n```\n\n'.format(obj.name, bases))
    if self.signature_code_block and obj.is_function():
      self._render_signature_block(fp, obj)
    if self.data_code_block and obj.is_data():
      self._render_data_block(fp, obj)
    if obj.docstring:
      lines = obj.docstring.split('\n')
      if self.docstrings_as_blockquote:
        lines = ['> ' + x for x in lines]
      fp.write('\n'.join(lines))
      fp.write('\n\n')

  def _render_recursive(self, fp, level, obj):
    self._render_object(fp, level, obj)
    for member in obj.members.values():
      self._render_recursive(fp, level+1, member)

  def _render(self, graph, fp):
    if self.render_toc:
      if self.render_toc_title:
        fp.write('# {}\n\n'.format(self.render_toc_title))
      for m in graph.modules:
        self._render_toc(fp, 0, m)
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

    if self.code_headers:
      if self.html_headers or self.sub_prefix:
        if self.sub_prefix and '.' in title:
          prefix, title = title.rpartition('.')[::2]
          title = '<sub>{}.</sub>{}'.format(prefix, title)
        title = '<code>{}</code>'.format(title)
      else:
        title = '`{}`'.format(title)
    else:
      title = obj.name
    if isinstance(obj, Module) and self.descriptive_module_title:
      title = 'Module ' + title
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

  def render_to_string(self, graph):
    fp = io.StringIO()
    self._render(graph, fp)
    return fp.getvalue()

  # Renderer

  def render(self, graph):
    if self.filename is None:
      self._render(graph, sys.stdout)
    else:
      with io.open(self.filename, 'w', encoding=self.encoding) as fp:
        self._render(graph, fp)
