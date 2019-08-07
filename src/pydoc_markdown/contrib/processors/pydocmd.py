
"""
Provides the #PydocmdProcessor class which converts the Pydoc-Markdown
highlighting syntax into Markdown.
"""

import re

from nr.types.structured import Field, Object
from nr.types.interface import implements
from pydoc_markdown.interfaces import Processor

# TODO @NiklasRosenstein Figure out a way to mark text linking to other
#     objects so that they can be properly handled by the renderer.


class PydocmdProcessorConfig(Object):
  pass


@implements(Processor)
class PydocmdProcessor(object):

  CONFIG_CLASS = PydocmdProcessorConfig

  def process(self, config, graph):
    graph.visit(self._process_node)

  def _process_node(self, node):
    if not getattr(node, 'docstring', None):
      return
    lines = []
    codeblock_opened = False
    current_section = None
    for line in node.docstring.split('\n'):
      if line.startswith("```"):
        codeblock_opened = (not codeblock_opened)
      if not codeblock_opened:
        line, current_section = self._preprocess_line(line, current_section)
      lines.append(line)
    node.docstring = self._preprocess_refs('\n'.join(lines))

  def _preprocess_line(self, line, current_section):
    match = re.match(r'# (.*)$', line)
    if match:
      current_section = match.group(1).strip().lower()
      line = re.sub(r'# (.*)$', r'__\1__\n', line)

    # TODO @NiklasRosenstein Parse type names in parentheses after the
    #     argument/attribute name.
    if current_section in ('arguments', 'parameters'):
      style = r'- __\1__:\3'
    elif current_section in ('attributes', 'members', 'raises'):
      style = r'- `\1`:\3'
    elif current_section in ('returns',):
      style = r'`\1`:\3'
    else:
      style = None
    if style:
      #                  | ident  | types     | doc
      line = re.sub(r'\s*([^\\:]+)(\s*\(.+\))?:(.*)$', style, line)

    return line, current_section

  def _preprocess_refs(self, content):
    def handler(match):
      ref = match.group('ref')
      parens = match.group('parens') or ''
      has_trailing_dot = False
      if not parens and ref.endswith('.'):
        ref = ref[:-1]
        has_trailing_dot = True
      result = '`{}`'.format(ref + parens)
      if has_trailing_dot:
        result += '.'
      return (match.group('prefix') or '') + result
    return re.sub('(?P<prefix>^| |\t)#(?P<ref>[\w\d\._]+)(?P<parens>\(\))?', handler, content)
