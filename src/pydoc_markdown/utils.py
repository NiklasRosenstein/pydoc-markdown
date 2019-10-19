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

import pkg_resources
from nr.types import abc


def import_object(name):
  module, member = name.rpartition('.')[::2]
  module = __import__(module, fromlist=[None])
  try:
    return getattr(module, member)
  except AttributeError:
    raise ImportError('Module "{}" has no member "{}"'.format(module, member))


def load_entry_point(group, name):
  """
  Returns the first entry point registered to the specified *group* that
  matches the *name*. If multiple entry points are registered to that name,
  an #EnvironmentError is raised.

  If no entry point with the specified *name* can be found, a #ValueError
  is raised instead.
  """

  result = None
  for ep in pkg_resources.iter_entry_points(group, name):
    if result is not None:
      raise EnvironmentError('multiple entry points registered to {}:{}'
        .format(group, name))
    result = ep
  if result is None:
    raise ValueError('no entry point registered to {}:{}'.format(group, name))
  return result


class EntrypointDict(abc.Mapping):

  def __init__(self, entrypoint_group):
    self._values = {}
    for ep in pkg_resources.iter_entry_points(entrypoint_group):
      self._values[ep.name] = ep

  def __getitem__(self, key):
    return self._values[key].load()

  def __len__(self):
    return len(self._values)

  def __iter__(self):
    return iter(self._values)
