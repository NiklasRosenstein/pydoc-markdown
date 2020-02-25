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

from nr.databind.core import Field, Struct, forward_decl
from typing import Optional

Argument = forward_decl()
Decorator = forward_decl()
Expression = forward_decl()
Object = forward_decl()


class Location(Struct):
  filename = Field(str)
  lineno = Field(int)


@forward_decl(Object)
class Object(Struct):
  location = Field(Location)
  parent = Field(Object, default=None)
  name = Field(str)
  docstring = Field(str, default=None)
  members = Field(dict, default=dict)

  def __init__(self, *args, **kwargs):
    super(Object, self).__init__(*args, **kwargs)
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
  decorators = Field([Decorator])
  bases = Field([Expression])
  metaclass = Field(Expression)


class Function(Object):
  is_async = Field(bool)
  decorators = Field([Decorator])
  args = Field([Argument])
  return_ = Field(Expression)

  @property
  def signature(self):
    return '{}({})'.format(self.name, Argument.format_arglist(self.args))

  @property
  def signature_args(self):
    return Argument.format_arglist(self.args)


class Data(Object):
  expr = Field(Expression)


@forward_decl(Decorator)
class Decorator(Struct):
  name = Field(str)
  args = Field(Expression, default=None)


@forward_decl(Argument)
class Argument(Struct):
  name = Field(str)
  annotation = Field(Expression, default=None)
  default = Field(Expression, default=None)
  type = Field(str)

  POS = 'pos'
  POS_REMAINDER = 'pos_remainder'
  KW_SEPARATOR = 'kw_separator'
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


@forward_decl(Expression)
class Expression(Struct):
  text = Field(str)

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
