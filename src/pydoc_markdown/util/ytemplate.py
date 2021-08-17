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
Template language for YAML files similar to [YTT][].

  [YTT]: https://get-ytt.io/
"""

from typing import Any, Dict, Mapping, TextIO, Type, Union
import textwrap
import json
import yaml


def load(
  file_: Union[str, TextIO],
  context: Dict[str, Any],
  Loader: Type[yaml.Loader] = None,  # TODO(@NiklasRosenstein): Correct type annotation
) -> Any:
  """
  Loads a YAML template into a Python object.

  # Arguments
  file_: The file-like object or filename to load.
  context: The context variables available to the template.
  Loader: The #yaml.Loader implementation. Defaults to #yaml.SafeLoader.
  """

  if isinstance(file_, str):
    with open(file_) as fp:
      return load(fp, context, Loader)

  if Loader is None:
    Loader = yaml.SafeLoader  # type: ignore

  yaml_code = []
  it = iter(file_)
  for line in it:

    # Parse Python code blocks.
    if line.startswith('#@'):
      block_lines = [line[2:]]
      for line in it:
        if not line.startswith('#@'):
          raise ValueError('missing #@ end')
        if line[2:].strip() == 'end':
          break
        block_lines.append(line[2:])
      code = textwrap.dedent(''.join(block_lines))
      exec(code, context, context)

    # Inline replacements.
    index = line.find('#@')
    if index > 0:
      line = line[:index] + json.dumps(eval(line[index+2:], context, context)) + '\n'

    yaml_code.append(line)

  return yaml.load(''.join(yaml_code), Loader)


class Attributor:

  def __init__(self, data: Mapping, default: Any = None) -> None:
    self._data = data
    self._default = default

  def __getattr__(self, name: str) -> Any:
    return self._data.get(name)
