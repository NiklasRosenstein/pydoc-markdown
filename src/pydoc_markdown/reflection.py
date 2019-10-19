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
This module provides the abstract representation of a code library. It is
generalised and intended to be usable for any language.
"""

from typing import Optional
from nr.types.struct import Struct, DefaultTypeMapper, set_type_mapper, AnyType
set_type_mapper(__name__, DefaultTypeMapper(fallback=AnyType()))


class Location(Struct):
  __annotations__ = [
    ('filename', str),
    ('lineno', int)
  ]


class Object(Struct):
  __annotations__ = [
    ('location', Location),
    ('parent', 'Object'),
    ('name', str),
    ('docstring', Optional[str]),
    ('members', dict, lambda: dict()),
  ]

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if self.parent is not None:
      if self.name in self.parent.members:
        self.parent.members[self.name].remove()
      self.parent.members[self.name] = self

  def __repr__(self):
    return '{}(name={!r}, members={!r})'.format(
      type(self).__name__, self.name, list(self.members.values()))

  def path(self, separator='.'):
    if not self.parent:
      return self.name
    else:
      return self.parent.path(separator) + separator + self.name

  def remove(self):
    if self.parent:
      assert self.parent.members[self.name] is self
      del self.parent.members[self.name]
      self.parent = None

  def is_module(self):
    return isinstance(self, Module)

  def is_class(self):
    return isinstance(self, Class)

  def is_data(self):
    return isinstance(self, Data)

  def is_function(self):
    return isinstance(self, Function)

  def is_method(self):
    if not self.parent:
      return False
    return isinstance(self, Function) and isinstance(self.parent, Class)

  def visit(self, func, allow_mutation=False):
    members = self.members.values()
    if allow_mutation:
      members = list(members)
    for child in members:
      child.visit(func, allow_mutation)
    func(self)


class Module(Object):
  pass


class Class(Object):
  __annotations__ = [
    ('decorators', 'List[Decorators]'),
    ('bases', 'List[Expression]'),
    ('metaclass', 'Expression'),
  ]


class Function(Object):
  __annotations__ = [
    ('is_async', bool),
    ('decorators', 'List[Decorator]'),
    ('args', 'List[Argument]'),
    ('return_', 'Expression')
  ]

  @property
  def signature(self):
    return '{}({})'.format(self.name, Argument.format_arglist(self.args))

  @property
  def signature_args(self):
    return Argument.format_arglist(self.args)


class Data(Object):
  __annotations__ = [
    ('expr', 'Expression')
  ]


class Decorator(Struct):
  __annotations__ = [
    ('name', str),
    ('args', 'Expression')
  ]


class Argument(Struct):
  __annotations__ = [
    ('name', str),
    ('annotation', 'Expression'),
    ('default', 'Expression'),
    ('type', str)
  ]

  POS = 'pos'
  POS_REMAINDER = 'pos_remainder'
  KW = 'kw'
  KW_ONLY = 'kw_only'
  KW_REMAINDER = 'kw_remainder'

  def __str__(self):
    parts = [self.name]
    if self.annotation:
      parts.append(': ' + str(self.annotation))
    if self.default:
      if self.annotation:
        parts.append(' ')
      parts.append('=')
    if self.default:
      if self.annotation:
        parts.append(' ')
      parts.append(str(self.default))
    if self.type == 'POS_REMAINDER':
      parts.insert(0, '*')
    elif self.type == 'KW_REMAINDER':
      parts.insert(0, '**')
    return ''.join(parts)

  @staticmethod
  def format_arglist(arglist):
    parts = []
    found_kw_only = False
    for arg in arglist:
      if not found_kw_only and arg.type == Argument.KW_ONLY:
        found_kw_only = True
        parts.append('*,')
      parts.append(str(arg))
    return ', '.join(parts)


class Expression(Struct):
  __annotations__ = [
    ('text', str)
  ]

  def __str__(self):
    return self.text


class ModuleGraph(object):
  """
  Represents a collection of #Module objects.
  """

  def __init__(self):
    self.modules = []

  def add_module(self, module):
    self.modules.append(module)

  def visit(self, func, allow_mutation=False):
    for module in self.modules:
      module.visit(func, allow_mutation)


__all__ = [
  'Location',
  'Module',
  'Class',
  'Function',
  'Data',
  'Decorator',
  'Argument',
  'Expression'
]
