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
This module provides utilities for importing Python objects by name.
"""


def import_module(name):
  """
  Imports a Python module assuming that the whole *name* identifies only a
  Python module and no symbol inside a Python module.
  """

  # fromlist must not be empty so we get the bottom-level module rather than
  # the top-level module.
  return __import__(name, fromlist=[''])


def import_object(name):
  """
  Like #import_object_with_scope() but returns only the object.
  """

  return import_object_with_scope(name)[0]


def import_object_with_scope(name):
  """
  Imports a Python object by an absolute identifier.

  # Arguments
  name (str): The name of the Python object to import.

  # Returns
  (any, Module): The object and the module that contains it. Note that
    for plain modules loaded with this function, both elements of the
    tuple may be the same object.
  """

  # Import modules until we can no longer import them. Prefer existing
  # attributes over importing modules at each step.
  parts = name.split('.')
  current_name = parts[0]
  obj = import_module(current_name)
  scope = None
  for part in parts[1:]:
    try:
      sub_obj = getattr(obj, part)
      scope, obj = obj, sub_obj
    except AttributeError:
      current_name += '.' + part
      obj = scope = import_module(current_name)
  return obj, scope
