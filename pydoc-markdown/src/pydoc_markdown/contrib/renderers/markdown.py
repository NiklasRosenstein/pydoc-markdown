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
import html
import io
import sys
import typing as t

import docspec
from docspec_python import format_arglist

from pydoc_markdown.interfaces import Context, Renderer, Resolver, SourceLinker
from pydoc_markdown.util.docspec import format_function_signature, is_method


@dataclasses.dataclass
class MarkdownRenderer(Renderer):
  """
  Produces Markdown files. This renderer is often used by other renderers, such as
  #MkdocsRenderer and #HugoRenderer. It provides a wide variety of options to customize
  the generated Markdown files.

  ### Options
  """

  #: The name of the file to render to. If no file is specified, it will
  #: render to stdout.
  filename: t.Optional[str] = None

  #: The encoding of the output file. This is ignored when rendering to
  #: stdout.
  encoding: str = 'utf-8'

  #: If enabled, inserts anchors before Markdown headers to ensure that
  #: links to the header work. This is enabled by default.
  insert_header_anchors: bool = True

  #: Generate HTML headers instead of Mearkdown headers. This is disabled
  #: by default.
  html_headers: bool = False

  #: Render names in headers as code (using backticks or `<code>` tags,
  #: depending on #html_headers). This is enabled by default.
  code_headers: bool = False

  #: Generate descriptive class titles by adding the word "Objects" after
  #: the class name. This is enabled by default.
  descriptive_class_title: bool = True

  #: Generate descriptivie module titles by adding the word "Module" before
  #: the module name. This is enabled by default.
  descriptive_module_title: bool = False

  #: Add the class name as a prefix to method names. This class name is
  #: also rendered as code if #code_headers is enabled. This is enabled
  #: by default.
  add_method_class_prefix: bool = False

  #: Add the class name as a prefix to member names. This is enabled by
  #: default.
  add_member_class_prefix: bool = False

  #: Add the full module name as a prefix to the title of the header.
  #: This is disabled by default.
  add_full_prefix: bool = False

  #: If #add_full_prefix is enabled, this will result in the prefix to
  #: be wrapped in a `<sub>` tag.
  sub_prefix: bool = False

  #: Render the definition of data members as a code block. This is disabled
  #: by default.
  data_code_block: bool = False

  #: Max length of expressions. If this limit is exceeded, the remaining
  #: characters will be replaced with three dots. This is set to 100 by
  #: default.
  data_expression_maxlength: int = 100

  #: Render the class signature as a code block. This includes the "class"
  #: keyword, the class name and its bases. This is enabled by default.
  classdef_code_block: bool = True

  #: Render the constructor signature in the class definition code block
  #: if its `__init__()` member is not visible.
  classdef_render_init_signature_if_needed: bool = True

  #: Render decorators before class definitions.
  classdef_with_decorators: bool = True

  #: Render classdef and function signature blocks in the Python help()
  #: style.
  signature_python_help_style: bool = False

  #: Render the function signature as a code block. This includes the "def"
  #: keyword, the function name and its arguments. This is enabled by
  #: default.
  signature_code_block: bool = True

  #: Render the function signature in the header. This is disabled by default.
  signature_in_header: bool = False

  #: Render the vertical bar '|' before function signature. This is enabled by default.
  signature_with_vertical_bar: bool = True

  #: Include the "def" keyword in the function signature. This is enabled
  #: by default.
  signature_with_def: bool = False

  #: Render the class name in the code block for function signature. Note
  #: that this results in invalid Python syntax to be rendered. This is
  #: disabled by default.
  signature_class_prefix: bool = False

  #: Render decorators before function definitions.
  signature_with_decorators: bool = True

  #: Add the string "python" after the backticks for code blocks. This is
  #: enabled by default.
  code_lang: bool = True

  #: Render a table of contents at the beginning of the file.
  render_toc: bool = False

  #: The title of the "Table of Contents" header.
  render_toc_title: str = 'Table of Contents'

  #: The maximum depth of the table of contents. Defaults to 2.
  toc_maxdepth: int = 2

  #: Render module headers. This is enabled by default.
  render_module_header: bool = True

  #: Custom template for module header.
  render_module_header_template: str = ''

  #: Render docstrings as blockquotes. This is disabled by default.
  docstrings_as_blockquote: bool = False

  #: Use a fixed header level for every kind of API object. The individual
  #: levels can be defined with #header_level_by_type.
  use_fixed_header_levels: bool = True

  #: Fixed header levels by API object type.
  header_level_by_type: t.Dict[str, int] = dataclasses.field(default_factory=lambda: {
    'Module': 1,
    'Class': 2,
    'Method': 4,
    'Function': 4,
    'Data': 4,
  })

  #: A plugin that implements the #SourceLinker interface to provide links to the
  #: source code of API objects. If this field is specified, the renderer will
  #: place links to the source code in the generated Markdown files.
  source_linker: t.Optional[SourceLinker] = None

  #: Allows you to define the position of the "view source" link in the Markdown
  #: file if a #source_linker is configured.
  # TODO: Validator.choices(["after signature", "before signature"])
  source_position: str = 'after signature'

  #: Allows you to override how the "view source" link is rendered into the Markdown
  #: file if a #source_linker is configured. The default is `[[view_source]]({url})`.
  source_format: str = '[[view_source]]({url})'

  #: Escape html in docstring. Default to False.
  escape_html_in_docstring: bool = False

  def __post_init__(self) -> None:
    self._resolver: t.Optional[MarkdownReferenceResolver] = MarkdownReferenceResolver([])

  def _get_parent(self, obj: docspec.ApiObject) -> t.Optional[docspec.ApiObject]:
    return self._resolver.reverse_map.get_parent(obj)

  def _is_method(self, obj: docspec.ApiObject) -> bool:
    return is_method(obj, self._resolver.reverse_map)

  def _format_arglist(self, func: docspec.Function) -> str:
    args = func.args[:]
    if self._is_method(func) and args and args[0].name == 'self':
      args.pop(0)
    return format_arglist(args)

  def _render_toc(self, fp, level, obj):
    if level > self.toc_maxdepth:
      return
    object_id = self._resolver.generate_object_id(obj)
    fp.write('  ' * level + '* [{}](#{})\n'.format(self._escape(obj.name), object_id))
    level += 1
    for child in getattr(obj, 'members', []):
      self._render_toc(fp, level, child)

  def _render_header(self, fp, level, obj):
    if self.render_module_header_template and isinstance(obj, docspec.Module):
      fp.write(
        self.render_module_header_template.format(
          module_name=obj.name,
          relative_module_name=obj.name.rsplit(".", 1)[-1]
        )
      )
      return

    object_id = self._resolver.generate_object_id(obj)
    if self.use_fixed_header_levels:
      # Read the header level based on the API object type. The default levels defined
      # in the field will act as a first fallback, the level of the object inside it's
      # hierarchy is the final fallback.
      type_name = 'Method' if self._is_method(obj) else type(obj).__name__
      level = self.header_level_by_type.get(type_name,
        type(self).__dataclass_fields__['header_level_by_type'].default_factory().get(type_name, level))
    if self.insert_header_anchors and not self.html_headers:
      fp.write('<a name="{}"></a>\n\n'.format(object_id))
    if self.html_headers:
      header_template = '<h{0} id="{1}">{{title}}</h{0}>'.format(level, object_id)
    else:
      header_template = level * '#' + ' {title}'
    fp.write(header_template.format(title=self._get_title(obj)))
    fp.write('\n\n')

  def _format_decorations(self, decorations: t.List[docspec.Decoration]) -> t.Iterable[str]:
    for dec in decorations:
      yield '@{}{}\n'.format(dec.name, dec.args or '')

  def _format_function_signature(self, func: docspec.Function, override_name: str = None, add_method_bar: bool = True) -> str:
    parts: t.List[str] = []
    if self.signature_with_decorators:
      parts += self._format_decorations(func.decorations)
    if self.signature_python_help_style and not self._is_method(func):
      parts.append('{} = '.format(func.path()))
    parts += [x + ' ' for x in func.modifiers or []]
    if self.signature_with_def:
      parts.append('def ')
    if self.signature_class_prefix and self._is_method(func):
      parent = self._get_parent(func)
      assert parent, func
      parts.append(parent.name + '.')
    parts.append((override_name or func.name))
    parts.append(format_function_signature(func, self._is_method(func)))
    result = ''.join(parts)
    if add_method_bar and self._is_method(func):
      result = '\n'.join(' | ' + l for l in result.split('\n'))
    return result

  def _format_classdef_signature(self, cls: docspec.Class) -> str:
    bases = ', '.join(map(str, cls.bases))
    if cls.metaclass:
      bases += ', metaclass=' + str(cls.metaclass)
    code = 'class {}({})'.format(cls.name, bases)
    if self.signature_python_help_style:
      code = cls.path() + ' = ' + code
    if self.classdef_render_init_signature_if_needed and '__init__' in cls.members:
      code += ':\n '
      if self.signature_with_vertical_bar:
        code += "|  "
      else:
        code += "   "

      code += self._format_function_signature(cls.members['__init__'], override_name=cls.name, add_method_bar=False)

    if cls.decorations and self.classdef_with_decorators:
      code = '\n'.join(self._format_decorations(cls.decorations)) + code
    return code

  def _format_data_signature(self, data: docspec.Data) -> str:
    expr = str(data.value)
    if len(expr) > self.data_expression_maxlength:
      expr = expr[:self.data_expression_maxlength] + ' ...'
    return data.name + ' = ' + expr

  def _render_signature_block(self, fp, obj):
    if self.classdef_code_block and isinstance(obj, docspec.Class):
      code = self._format_classdef_signature(obj)
    elif self.signature_code_block and isinstance(obj, docspec.Function):
      code = self._format_function_signature(obj, add_method_bar=self.signature_with_vertical_bar)
    elif self.data_code_block and isinstance(obj, docspec.Data):
      code = self._format_data_signature(obj)
    else:
      return
    fp.write('```{}\n'.format('python' if self.code_lang else ''))
    fp.write(code)
    fp.write('\n```\n\n')

  def _render_object(self, fp, level, obj):
    if not isinstance(obj, docspec.Module) or self.render_module_header:
      self._render_header(fp, level, obj)
    url = self.source_linker.get_source_url(obj) if self.source_linker else None
    source_string = self.source_format.replace('{url}', str(url)) if url else None
    if source_string and self.source_position == 'before signature':
      fp.write(source_string + '\n\n')
    self._render_signature_block(fp, obj)
    if source_string and self.source_position == 'after signature':
      fp.write(source_string + '\n\n')
    if obj.docstring:
      docstring = html.escape(obj.docstring) if self.escape_html_in_docstring else obj.docstring
      lines = docstring.split('\n')
      if self.docstrings_as_blockquote:
        lines = ['> ' + x for x in lines]
      fp.write('\n'.join(lines))
      fp.write('\n\n')

  def _render_recursive(self, fp, level, obj):
    self._render_object(fp, level, obj)
    level += 1
    for member in getattr(obj, 'members', []):
      self._render_recursive(fp, level, member)

  def _get_title(self, obj: docspec.ApiObject) -> str:
    title = obj.name
    if (self.add_method_class_prefix and self._is_method(obj)) or \
       (self.add_member_class_prefix and isinstance(obj, docspec.Data)):
      title = self._get_parent(obj).name + '.' + title
    elif self.add_full_prefix and not self._is_method(obj):
      title = obj.path()

    if isinstance(obj, docspec.Function):
      if self.signature_in_header:
        title += '(' + self._format_arglist(obj) + ')'

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
    if isinstance(obj, docspec.Module) and self.descriptive_module_title:
      title = 'Module ' + title
    if isinstance(obj, docspec.Class) and self.descriptive_class_title:
      title += ' Objects'
    return title

  def _escape(self, s):
    return s.replace('_', '\\_').replace('*', '\\*')

  def render_to_string(self, modules: t.List[docspec.Module]) -> str:
    fp = io.StringIO()
    self.render_to_stream(modules, fp)
    return fp.getvalue()

  def render_to_stream(self, modules: t.List[docspec.Module], stream: t.TextIO):
    self._resolver = MarkdownReferenceResolver(modules)

    if self.render_toc:
      if self.render_toc_title:
        stream.write('# {}\n\n'.format(self.render_toc_title))
      for m in modules:
        self._render_toc(stream, 0, m)
      stream.write('\n')
    for m in modules:
      self._render_recursive(stream, 1, m)

  # Renderer

  def get_resolver(self, modules: t.List[docspec.Module]) -> t.Optional[Resolver]:
    """
    Returns a simple #Resolver implementation. Finds cross-references in the same file.
    """

    return MarkdownReferenceResolver(modules)

  def render(self, modules: t.List[docspec.Module]) -> None:
    if self.filename is None:
      self.render_to_stream(modules, sys.stdout)
    else:
      with io.open(self.filename, 'w', encoding=self.encoding) as fp:
        self.render_to_stream(modules, t.cast(t.TextIO, fp))

  # PluginBase

  def init(self, context: Context) -> None:
    if self.source_linker:
      self.source_linker.init(context)


class MarkdownReferenceResolver(Resolver):

  def __init__(self, modules: t.List[docspec.ApiObject]) -> None:
    self.reverse_map = docspec.ReverseMap(modules)

  def generate_object_id(self, obj):
    parts = []
    while obj:
      parts.append(obj.name)
      obj = self.reverse_map.get_parent(obj)
    return '.'.join(reversed(parts))

  def _resolve_reference(self, obj: docspec.ApiObject, ref: t.List[str]) -> t.Optional[docspec.ApiObject]:
    for part_name in ref:
      obj = docspec.get_member(obj, part_name)
      if not obj:
        return None
    return obj

  def _find_reference(self, obj: docspec.ApiObject, ref: t.List[str]) -> t.Optional[docspec.ApiObject]:
    while obj:
      resolved = self._resolve_reference(obj, ref)
      if resolved:
        return resolved
      obj = self.reverse_map.get_parent(obj)
    return None

  def resolve_ref(self, obj: docspec.ApiObject, ref: str) -> t.Optional[str]:
    target = self._find_reference(obj, ref.split('.'))
    if target:
      return '#' + self.generate_object_id(target)
    return None
