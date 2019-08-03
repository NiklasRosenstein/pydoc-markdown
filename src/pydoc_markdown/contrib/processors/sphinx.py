
"""
Provides the #SphinxProcessor that converts reST/Sphinx syntax to
markdown compatible syntax.
"""

import re

from nr.types.structured import Field, Object
from nr.types.interface import implements
from pydoc_markdown.interfaces import Processor


class SphinxProcessorConfig(Object):
  pass


class SphinxProcessor(Preprocessor):

  def get_config_class(self):
    return SphinxProcessorConfig

  def preprocess(self, root, node):
    if not node.docstring:
      return
    lines = []
    in_codeblock = False
    keyword = None
    components = {}

    for line in node.docstring.split('\n'):
      line = line.strip()

      if line.startswith("```"):
        in_codeblock = not in_codeblock

      if not in_codeblock:
        match = re.match(r':(?:param|parameter)\s+(\w+)\s*:(.*)?$', line)
        if match:
          keyword = 'Arguments'
          param = match.group(1)
          text = match.group(2)
          text = text.strip()

          component = components.get(keyword, [])
          component.append('- `{}`: {}'.format(param, text))
          components[keyword] = component
          continue

        match = re.match(r':(?:return|returns)\s*:(.*)?$', line)
        if match:
          keyword = 'Returns'
          text = match.group(1)
          text = text.strip()

          component = components.get(keyword, [])
          component.append(text)
          components[keyword] = component
          continue

        match = re.match(':(?:raises|raise)\s+(\w+)\s*:(.*)?$', line)
        if match:
          keyword = 'Raises'
          exception = match.group(1)
          text = match.group(2)
          text = text.strip()

          component = components.get(keyword, [])
          component.append('- `{}`: {}'.format(exception, text))
          components[keyword] = component
          continue

      if keyword is not None:
        components[keyword].append(line)
      else:
        lines.append(line)

    for key in components:
      self._append_section(lines, key, components)

    node.docstring = '\n'.join(lines)

  @staticmethod
  def _append_section(lines, key, sections):
    section = sections.get(key)
    if not section:
      return

    if lines and lines[-1]:
      lines.append('')

    lines.extend(['**{}**:'.format(key), ''])  # add an extra line because of markdown syntax
    lines.extend(section)

