
"""
Implements a renderer that produces Markdown output.
"""

import io
import nr.config
import sys

from ..parse.reflection import *
from . import Renderer


@nr.config.underscores_to_dashes
class MarkdownRendererConfig(nr.config.Partial):
  __fields__ = [
    ('filename', str, None),
    ('encoding', str, 'utf8'),
    ('html_headings', bool, False),
    ('code_headings', bool, True),
    ('descriptive_class_title', bool, True),
    ('add_method_class_prefix', bool, True),
    ('add_full_prefix', bool, False),
    ('sub_prefix', bool, False),
    ('signature_below_heading', bool, True),
    ('signature_in_heading', bool, False)
  ]


class MarkdownRenderer(Renderer):

  config_class = MarkdownRendererConfig

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
      fp.write('\n````\n\n')
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

  def render(self, modules):
    if self.config.filename is None:
      for m in modules:
        self.render_recursive(sys.stdout, 1, m)
    else:
      with io.open(self.config.filename, 'w', encoding=self.config.encoding) as fp:
        self.render_recursive(fp, 1, m)


renderer_class = MarkdownRenderer
