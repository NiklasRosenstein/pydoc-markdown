
"""
Implements a renderer that produces Markdown output.
"""

from __future__ import print_function
from ..parsing.reflection import *


class MarkdownRenderer(object):

  def __init__(self, html_headings=False, code_headings=True):
    self.html_headings = html_headings
    self.code_headings = code_headings

  def render_object(self, fp, level, obj):
    if self.html_headings:
      heading_template = '<h{}>{{title}}</h{}>'.format(level)
      if self.code_headings:
        heading_template = heading_template.format(
          title='<code>{title}</code>')
    else:
      heading_template = level * '#' + ' {title}'
      if self.code_headings:
        heading_template = heading_template.format(
          title='`{title}`')
    fp.write(heading_template.format(title=obj.name))
    fp.write('\n\n')
    if obj.docstring:
      fp.write(obj.docstring)
    fp.write('\n\n')

  def render_recursive(self, fp, level, obj):
    self.render_object(fp, level, obj)
    for member in obj.members.values():
      self.render_recursive(fp, level+1, member)
