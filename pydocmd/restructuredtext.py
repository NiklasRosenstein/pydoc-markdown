# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
This module implements preprocessing Markdown-like docstrings and converts
it to fully markdown compatible markup.
"""

import re


class Preprocessor(object):
  """
  This class implements the preprocessor for restructured text.
  """
  _SECTION_MAP = {'param': 'Arguments', 'return': 'Returns', 'raises': 'Raises'}

  def preprocess_section(self, section):
    """
    Preprocessors a given section into it's components.
    """
    lines = []
    in_codeblock = False
    keyword = None
    components = {}
    for line in section.content.split('\n'):
      line = line.strip()

      if line.startswith("```"):
        in_codeblock = not in_codeblock

      if in_codeblock:
        lines.append(line)
        continue

      match = re.match(r':(param)\s+(\w+):(.*)$', line)
      if match:
        keyword = match.group(1)
        param = match.group(2)
        text = match.group(3)
        text = text.strip()

        component = components.get(keyword, [])
        component.append('- `{}`: {}'.format(param, text))
        components[keyword] = component
        continue

      match = re.match(r':(return):\s+(.*)$', line)
      if match:
        keyword = match.group(1)
        text = match.group(2)
        text = text.strip()

        component = components.get(keyword, [])
        component.append(text)
        components[keyword] = component
        continue

      match = re.match(':(raises)\s+(\w+):(.*)$', line)
      if match:
        keyword = match.group(1)
        param = match.group(2)
        text = match.group(3)
        text = text.strip()

        component = components.get(keyword, [])
        component.append('- `{}`: {}'.format(param, text))
        components[keyword] = component
        continue

      if keyword is not None:
        components[keyword].append(line)
      else:
        lines.append(line)

    for component in ['param', 'return', 'raises']:
      self._append_section(lines, component, components)

    section.content = '\n'.join(lines)

  def _append_section(self, lines, key, sections):
    section = sections.get(key)
    if not section:
      return

    if lines and lines[-1]:
      lines.append('')

    lines.extend(['**{}**:'.format(self._SECTION_MAP[key]), ''])  # add an extra line because of markdown syntax
    lines.extend(section)
