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
import logging
import re
import typing as t

import docspec

from pydoc_markdown.interfaces import Processor, Resolver

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class _ParamLine:
  """
  Helper data class for holding details of Sphinx arguments.
  """

  name: str
  docs: str
  type: t.Optional[str] = None


def generate_sections_markdown(lines, sections):
  for key, section in sections.items():
    if lines and lines[-1]:
      lines.append('')

    lines.extend(['**{}**:'.format(key), ''])  # add an extra line because of markdown syntax
    lines.extend(section)


@dataclasses.dataclass
class SphinxProcessor(Processor):
  """
  This processor parses ReST/Sphinx-style function documentation and converts it into
  Markdown syntax.

  Example:

  ```
  :param arg1: This is the first argument.
  :raise ValueError: If *arg1* is a bad value.
  :return: An `int` that represents an interesting value.
  ```

  Renders as:

  :param arg1: This is the first argument.
  :raise ValueError: If *arg1* is a bad value.
  :return: An `int` that represents an interesting value.

  @doc:fmt:sphinx
  """

  def check_docstring_format(self, docstring: str) -> bool:
    return ':param' in docstring or ':return' in docstring or \
      ':raise' in docstring

  def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
    docspec.visit(modules, self._process)

  def _process(self, node):
    if not node.docstring:
      return

    lines = []
    in_codeblock = False
    keyword = None
    components: t.Dict[str, t.List[str]] = {}
    parameters: t.List[_ParamLine] = []
    return_: t.Optional[_ParamLine] = None

    for line in node.docstring.split('\n'):
      if line.strip().startswith("```"):
        in_codeblock = not in_codeblock

      line_codeblock = line.startswith('    ')

      if not in_codeblock and not line_codeblock:
        line = line.strip()
        match = re.match(r'\s*:(arg|argument|param|parameter|type)\s+(\w+)\s*:(.*)?$', line)
        if match:
          keyword = 'Arguments'
          components.setdefault(keyword, [])
          param = match.group(2)
          text = match.group(3)
          text = text.strip()
          param_data = next((p for p in parameters if p.name == param), None)
          if match.group(1) == 'type':
            if param_data is None:
              param_data = _ParamLine(param, '', text)
              parameters.append(param_data)
            else:
              param_data.type = text
          else:
            if param_data is None:
              param_data = _ParamLine(param, text, None)
              parameters.append(param_data)
            else:
              param_data.docs = text
          continue

        match = re.match(r'\s*:(return|returns|rtype)\s*:(.*)?$', line)
        if match:
          keyword = 'Returns'
          components.setdefault('Returns', [])
          text = match.group(2)
          text = text.strip()
          if match.group(1) == 'rtype':
            if return_ is None:
              return_ = _ParamLine('return', '', text)
            else:
              return_.type = text
          else:
            if return_ is None:
              return_ = _ParamLine('return', text, None)
            else:
              return_.docs = text
          continue

        match = re.match('\\s*:(?:raises|raise)\\s+(\\w+)\\s*:(.*)?$', line)
        if match:
          keyword = 'Raises'
          exception = match.group(1)
          text = match.group(2)
          text = text.strip()

          component = components.setdefault(keyword, [])
          component.append('- `{}`: {}'.format(exception, text))
          continue

      if keyword is not None:
        components[keyword].append(line)
      else:
        lines.append(line)

    # Convert the parameters into actual markdown format.
    component = components['Arguments'] if parameters else []
    for param in parameters:
      if param.type:
        component.append('- `{}` (`{}`): {}'.format(param.name, param.type, param.docs))
      else:
        component.append('- `{}`: {}'.format(param.name, param.docs))

    # Convert the return data into markdown format.
    if return_:
      return_fmt = f'`{return_.type}`: {return_.docs}' if return_.type else return_.docs
      components['Returns'] = [return_fmt]

    generate_sections_markdown(lines, components)
    node.docstring = '\n'.join(lines)
