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
  This class implements the basic preprocessing.
  """

  def __init__(self, config):
    self.config = config

  def preprocess_section(self, section):
    """
    Preprocess the contents of *section*.
    """
    codeblock_opened = False
    current_section = None
    content = self._preprocess_refs(section)
    lines = []
    for line in content.split('\n'):
      if line.startswith("```"):
        codeblock_opened = (not codeblock_opened)
      if not line:
        current_section = None
      elif not codeblock_opened:
        line, current_section = self._preprocess_line(line, current_section)
      lines.append(line)
    section.content = '\n'.join(lines)

  def _preprocess_line(self, line, current_section):
    match = re.match(r'# (.*)$', line)
    if match:
      current_section = match.group(1).strip().lower()
      line = re.sub(r'# (.*)$', r'__\1__\n', line)

    # TODO: Parse type names in parentheses after the argument/attribute name.
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

  def _preprocess_refs(self, section):
    """
    Parses references and replaces them with markdown links
    Syntax is:
        `#anchor` for in page reference
        `#::mod[.submod][#item][+n]` where
            `mod.submod` is the module, `item` is the module member and n is
            the number of duplicates in case of headers: markdown conflicts.
            You can also references class members: `#::mod.submod.cls#method`
    """
    def handler(match):
      mod = match.group('mod')
      ref = match.group('ref')
      parens = match.group('parens') or ''
      dup = match.group('dup')
      has_trailing_dot = False
      if not parens and ref.endswith('.'):
        ref = ref[:-1]
        has_trailing_dot = True

      if '#' in ref:
        text = ref.split('#')[-1]
        title = mod_ref = ref.replace('#', '.')
        anchor = text.lower()
      else:
        title = text = anchor = ref
        anchor = ref.replace('.', '')
        mod_ref = ref

      if self.config['headers'] == 'html':
          anchor = mod_ref
          if not mod and not anchor.startswith(section.identifier):
              anchor = section.identifier + '.' + anchor
      elif dup:
          anchor += '_' + dup[1:]

      result = '`{}`'.format(text + parens)
      link = self.link_lookup.get(mod_ref, self.link_lookup.get(ref))
      if mod and link:
        result = ('[' + result + '](' + link + '#' + anchor + ' "' + title + '")')
      else:
        result = '[' + result + '](#' + anchor + ')'
      if has_trailing_dot:
        result += '.'
      return (match.group('prefix') or '') + result
    return re.sub('(?P<prefix>^| |\t)#(?P<mod>::)?(?P<ref>[\w\d\._\#]+)(?P<parens>\(\))?(?P<dup>\+\d+)?', handler, section.content)
