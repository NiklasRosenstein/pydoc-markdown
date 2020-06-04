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

from nr.databind.core import Field, Struct
from nr.interface import implements
from pydoc_markdown.interfaces import Renderer, Resolver
from pydoc_markdown.reflection import Object, Class, Data, Function, Module, ModuleGraph
from typing import Optional
import io
import sys


@implements(Renderer)
class MarkdownRenderer(Struct):
  #: Can be used to explicitly specify a file object to render to.
  fp = Field(object, default=None, hidden=True)

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
  code_headers = Field(bool, default=False)

  #: Generate descriptive class titles by adding the word "Objects" after
  #: the class name. This is enabled by default.
  descriptive_class_title = Field(bool, default=True)

  #: Generate descriptivie module titles by adding the word "Module" before
  #: the module name. This is enabled by default.
  descriptive_module_title = Field(bool, default=False)

  #: Add the class name as a prefix to method names. This class name is
  #: also rendered as code if #code_headers is enabled. This is enabled
  #: by default.
  add_method_class_prefix = Field(bool, default=False)

  #: Add the class name as a prefix to member names. This is enabled by
  #: default.
  add_member_class_prefix = Field(bool, default=False)

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

  #: Render the constructor signature in the class definition code block
  #: if its `__init__()` member is not visible.
  classdef_render_init_signature_if_needed = Field(bool, default=True)

  #: Render classdef and function signature blocks in the Python help()
  #: style.
  signature_python_help_style = Field(bool, default=False)

  #: Render the function signature as a code block. This includes the "def"
  #: keyword, the function name and its arguments. This is enabled by
  #: default.
  signature_code_block = Field(bool, default=True)

  #: Render the function signature in the header. This is disabled by default.
  signature_in_header = Field(bool, default=False)

  #: Include the "def" keyword in the function signature. This is enabled
  #: by default.
  signature_with_def = Field(bool, default=False)

  #: Render the class name in the code block for function signature. Note
  #: that this results in invalid Python syntax to be rendered. This is
  #: disabled by default.
  signature_class_prefix = Field(bool, default=False)

  #: Add the string "python" after the backticks for code blocks. This is
  #: enabled by default.
  code_lang = Field(bool, default=True)

  #: Render a table of contents at the beginning of the file.
  render_toc = Field(bool, default=False)

  #: The title of the "Table of Contents" header.
  render_toc_title = Field(str, default='Table of Contents')

  #: The maximum depth of the table of contents. Defaults to 2.
  toc_maxdepth = Field(int, default=2)

  #: Render module headers. This is enabled by default.
  render_module_header = Field(bool, default=True)

  #: Render docstrings as blockquotes. This is disabled by default.
  docstrings_as_blockquote = Field(bool, default=False)

  #: Use a fixed header level for every kind of API object. The individual
  #: levels can be defined with #header_level_by_type.
  use_fixed_header_levels = Field(bool, default=True)

  #: Fixed header levels by API object type.
  header_level_by_type = Field({int}, default={
    'Module': 1,
    'Class': 2,
    'Method': 4,
    'Function': 4,
    'Data': 4,
  })

  def _render_toc(self, fp, level, obj):
    if level > self.toc_maxdepth:
      return
    if obj.visible:
      object_id = self._generate_object_id(obj)
      fp.write('  ' * level + '* [{}](#{})\n'.format(self._escape(obj.name), object_id))
      level += 1
    for child in obj.members.values():
      self._render_toc(fp, level, child)

  def _render_header(self, fp, level, obj):
    object_id = self._generate_object_id(obj)
    if self.use_fixed_header_levels:
      level = self.header_level_by_type.get(type(obj).__name__, level)
    if self.insert_header_anchors and not self.html_headers:
      fp.write('<a name="{}"></a>\n'.format(object_id))
    if self.html_headers:
      header_template = '<h{0} id="{1}">{{title}}</h{0}>'.format(level, object_id)
    else:
      header_template = level * '#' + ' {title}'
    fp.write(header_template.format(title=self._get_title(obj)))
    fp.write('\n\n')

  def _format_function_signature(self, func: Function, override_name: str = None, add_method_bar: bool = True) -> str:
    parts = []
    for dec in func.decorators:
      parts.append('@{}{}\n'.format(dec.name, dec.args or ''))
    if self.signature_python_help_style and not func.is_method():
      parts.append('{} = '.format(func.path()))
    if func.is_async:
      parts.append('async ')
    if self.signature_with_def:
      parts.append('def ')
    if self.signature_class_prefix and (
        func.is_function() and func.parent and func.parent.is_class()):
      parts.append(func.parent.name + '.')
    parts.append((override_name or func.name))
    parts.append('(' + func.signature_args + ')')
    if func.return_:
      parts.append(' -> {}'.format(func.return_))
    result = ''.join(parts)
    if add_method_bar and func.is_method():
      result = '\n'.join(' | ' + l for l in result.split('\n'))
    return result

  def _format_classdef_signature(self, cls: Class) -> str:
    bases = ', '.join(map(str, cls.bases))
    if cls.metaclass:
      bases += ', metaclass=' + str(cls.metaclass)
    code = 'class {}({})'.format(cls.name, bases)
    if self.signature_python_help_style:
      code = cls.path() + ' = ' + code
    if self.classdef_render_init_signature_if_needed and (
        '__init__' in cls.members and not cls.members['__init__'].visible):
      code += ':\n |  ' + self._format_function_signature(
        cls.members['__init__'], override_name=cls.name, add_method_bar=False)
    return code

  def _format_data_signature(self, data: Data) -> str:
    expr = str(data.expr)
    if len(expr) > self.data_expression_maxlength:
      expr = expr[:self.data_expression_maxlength] + ' ...'
    return data.name + ' = ' + expr

  def _render_signature_block(self, fp, obj):
    if self.classdef_code_block and obj.is_class():
      code = self._format_classdef_signature(obj)
    elif self.signature_code_block and obj.is_function():
      code = self._format_function_signature(obj)
    elif self.data_code_block and obj.is_data():
      code = self._format_data_signature(obj)
    else:
      return
    fp.write('```{}\n'.format('python' if self.code_lang else ''))
    fp.write(code)
    fp.write('\n```\n\n')

  def _render_object(self, fp, level, obj):
    if not isinstance(obj, Module) or self.render_module_header:
      self._render_header(fp, level, obj)
    self._render_signature_block(fp, obj)
    if obj.docstring:
      lines = obj.docstring.split('\n')
      if self.docstrings_as_blockquote:
        lines = ['> ' + x for x in lines]
      fp.write('\n'.join(lines))
      fp.write('\n\n')

  def _render_recursive(self, fp, level, obj):
    if obj.visible:
      self._render_object(fp, level, obj)
      level += 1
    for member in obj.members.values():
      self._render_recursive(fp, level, member)

  def _render_graph(self, graph, fp):
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
    if (self.add_method_class_prefix and obj.is_method()) or \
       (self.add_member_class_prefix and obj.is_data()):
      title = obj.parent.name + '.' + title
    elif self.add_full_prefix and not obj.is_method():
      title = obj.path()

    if obj.is_function():
      if self.signature_in_header:
        title += '(' + obj.signature_args + ')'

    if self.code_headers:
      if self.html_headers or self.sub_prefix:
        if self.sub_prefix and '.' in title:
          prefix, title = title.rpartition('.')[::2]
          title = '<sub>{}.</sub>{}'.format(prefix, title)
        title = '<code>{}</code>'.format(title)
      else:
        title = '`{}`'.format(title)
    else:
      title = self._escape(title)
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

  def render_to_string(self, graph: ModuleGraph):
    fp = io.StringIO()
    self._render_graph(graph, fp)
    return fp.getvalue()

  # Renderer

  def get_resolver(self, graph: ModuleGraph) -> Resolver:
    def resolver(scope: Object, ref: str) -> Optional[str]:
      target = graph.resolve_ref(scope, ref.split('.'))
      if target:
        return '#' + self._generate_object_id(target)
      return None
    return Resolver(resolver)

  def render(self, graph: ModuleGraph):
    if self.filename is None:
      self._render_graph(graph, self.fp or sys.stdout)
    else:
      with io.open(self.filename, 'w', encoding=self.encoding) as fp:
        self._render_graph(graph, fp)
