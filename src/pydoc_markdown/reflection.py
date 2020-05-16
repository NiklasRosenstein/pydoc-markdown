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

from nr.databind.core import Field, Struct, ProxyType
from typing import List, Optional

Argument = ProxyType()
Decorator = ProxyType()
Expression = ProxyType()
Object = ProxyType()


class Location(Struct):
  filename = Field(str)
  lineno = Field(int)

  def __str__(self):
    return '{}:{}'.format(self.filename, self.lineno)


@Object.implementation  # pylint: disable=function-redefined
class Object(Struct):
  location = Field(Location, nullable=True)
  parent = Field(Object, default=None)
  name = Field(str)
  docstring = Field(str, default=None)
  members = Field(dict, default=dict)
  visible = Field(bool, default=True)

  def __init__(self, *args, **kwargs):
    super(Object, self).__init__(*args, **kwargs)
    if self.parent is not None:
      if self.name in self.parent.members:
        self.parent.members[self.name].remove()
      self.parent.members[self.name] = self

  def __repr__(self):
    v = ['{}={!r}'.format(k, getattr(self, k)) for k in self.__fields__
         if k not in ('location', 'parent', 'docstring', 'members')]
    return '{}({})'.format(type(self).__name__, ', '.join(v))

  def path(self, separator='.'):
    if not self.parent or isinstance(self.parent, ModuleGraph):
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
  decorators = Field([Decorator], nullable=True)
  bases = Field([Expression])
  metaclass = Field(Expression, nullable=True)


class Function(Object):
  is_async = Field(bool)
  decorators = Field([Decorator])
  args = Field([Argument])
  return_ = Field(Expression, nullable=True)

  @property
  def signature(self):
    return '{}({})'.format(self.name, Argument.format_arglist(self.args))

  @property
  def signature_args(self):
    if self.is_method and self.args and self.args[0].name == 'self':
      return Argument.format_arglist(self.args[1:])
    return Argument.format_arglist(self.args)


class Data(Object):
  expr = Field(Expression, default=None)
  annotation = Field(Expression, default=None)


@Decorator.implementation  # pylint: disable=function-redefined
class Decorator(Struct):
  name = Field(str)
  args = Field(Expression, default=None)


@Argument.implementation  # pylint: disable=function-redefined
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
    if self.type == Argument.KW_SEPARATOR:
      return '*'
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
    if self.type == Argument.POS_REMAINDER:
      parts.insert(0, '*')
    elif self.type == Argument.KW_REMAINDER:
      parts.insert(0, '**')
    return ''.join(parts)

  @staticmethod
  def format_arglist(arglist):
    parts = []
    for arg in arglist:
      parts.append(str(arg))
    return ', '.join(parts)


@Expression.implementation  # pylint: disable=function-redefined
class Expression(Struct):
  text = Field(str)

  def __str__(self):
    return self.text


class ModuleGraph(Object):
  """
  Represents a collection of #Object#s, typically #Module#s.
  """

  # TODO (@NiklasRosenstein): Change "module" naming to "node".

  def __init__(self, nodes=()):
    super().__init__(
      location=None,
      parent=None,
      name='',
      docstring=None,
      members={})
    for node in nodes:
      self.add_module(node)

  @property
  def modules(self):
    return list(self.members.values())

  def add_module(self, node):
    self.members[node.name] = node
    node.parent = self

  def resolve_ref(self, scope: Object, ref: List[str]) -> Optional[Object]:
    """ Resolve a reference to another object from within the specified
    *scope*. Returns the target, or None if the target cannot be resolved
    from the ref.

    The *ref* must be a list of names that can be retrieved from the scope's
    members in order. If no scope is specified, it will be resolved inside
    the #ModuleGraph. """

    if not ref:
      return None

    def _single_resolve(scope, ref):
      for name in ref:
        if name not in scope.members:
          return None
        scope = scope.members[name]
      return scope

    while scope:
      target = _single_resolve(scope, ref)
      if target:
        return target
      scope = scope.parent

    fake = Object(location=None, name='fake', members={x.name: x for x in self.modules})
    return _single_resolve(fake, ref)


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
