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

from nr.databind.core.union import (
  IUnionTypeMember,
  IUnionTypeResolver,
  UnknownUnionTypeError,
)
from nr.interface import implements
from nr.pylang.utils import classdef
from typing import Any, Iterable


@implements(IUnionTypeResolver)
class ChainTypeResolver:
  """
  Chain multiple #IUnionTypeResolver instances.
  """

  classdef.comparable('_resolvers')

  def __init__(self, *resolvers: IUnionTypeResolver) -> None:
    self._resolvers = resolvers

  def resolve(self, type_name: str) -> IUnionTypeMember:
    for resolver in self._resolvers:
      try:
        return resolver.resolve(type_name)
      except UnknownUnionTypeError:
        pass
    raise UnknownUnionTypeError(type_name)

  def reverse(self, value: Any) -> IUnionTypeMember:
    for resolver in self._resolvers:
      try:
        return resolver.reverse(value)
      except UnknownUnionTypeError:
        pass
    raise UnknownUnionTypeError(type(value))

  def members(self) -> Iterable[IUnionTypeMember]:
    has_members = False
    for resolver in self._resolvers:
      try:
        yield from resolver.members()
        has_members = True
      except NotImplementedError:
        pass
    if not has_members:
      raise NotImplementedError
