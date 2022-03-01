
from __future__ import annotations

import typing as t
import typing_extensions as te

import docspec
import docspec_python

from nr.util.generic import T
from nr.util import Stream


def get_members_of_type(objs: t.Union[docspec.ApiObject, t.List[docspec.ApiObject]], type_: t.Type[T]) -> t.List[T]:
  if isinstance(objs, docspec.HasMembers):
    return [x for x in objs.members if isinstance(x, type_)]
  elif isinstance(objs, docspec.ApiObject):
    return []
  else:
    return Stream(get_members_of_type(x, type_) for x in objs).concat().collect()


def format_function_signature(func: docspec.Function, exclude_self: bool = False) -> str:
  assert isinstance(func, docspec.Function), type(func)
  args = func.args[:]
  if exclude_self and args and args[0].name == 'self':
    args.pop(0)
  sig = f'({docspec_python.format_arglist(args)})'
  if func.return_type:
    sig += f' -> {func.return_type}'
  return sig


def is_function(obj: docspec.ApiObject) -> te.TypeGuard[docspec.Function]:
  return isinstance(obj, docspec.Function)


def is_method(obj: docspec.ApiObject) -> te.TypeGuard[docspec.Function]:
  return is_function(obj) and isinstance(obj.parent, docspec.Class)


def is_property(obj: docspec.ApiObject) -> te.TypeGuard[docspec.Function]:
  return is_function(obj) and any(d.name == 'property' for d in obj.decorations or [])


def is_attr(obj: docspec.ApiObject) -> te.TypeGuard[docspec.Variable]:
  return isinstance(obj, docspec.Variable) and isinstance(obj.parent, docspec.Class)


def get_object_description(obj: docspec.ApiObject) -> str:
  """
  Determines the best matching description of *obj*. Returns a string such as "module", "class", "abstract class",
  "enum", "attribute", "property", "function", "method", "abstract method", "class method", "static method" and
  "abstract class method".
  """

  if isinstance(obj, docspec.Module):
    return 'module'
  elif isinstance(obj, docspec.Class):
    if any(x in (obj.bases or ()) for x in ('abc.ABC', 'ABC')) or \
       any(x in (obj.metaclass or ()) for x in ('abc.ABCMeta', 'ABCMeta')):
      return 'abstract class'
    return 'class'
  elif isinstance(obj, docspec.Function):
    if any(x.name == 'property' for x in obj.decorations or []):
      return 'property'
    if any(x.name in ('abc.abstractproperty', 'abstractproperty') for x in obj.decorations or []):
      return 'abstract property'
    if any(x.name in ('abc.abstractmethod', 'abstractmethod') for x in obj.decorations or []):
      return 'abstract method'
    if any(x.name in ('abc.abstractclassmethod', 'abstractclassmethod') for x in obj.decorations or []):
      return 'abstract class method'
    if any(x.name == 'classmethod' for x in obj.decorations or []):
      return 'class method'
    if any(x.name == 'staticmethod' for x in obj.decorations or []):
      return 'static method'
    if is_method(obj):
      return 'method'
    return 'function'
  elif isinstance(obj, docspec.Variable):
    if is_attr(obj):
      return 'attribute'
    return 'data'
  else:
    assert False, type(obj)


class ApiSuite:
  """ Container for all loaded API objects. """

  def __init__(self, modules: t.List[docspec.Module]) -> None:
    self._modules = modules

  def resolve_fqn(self, fqn: str) -> t.List[docspec.ApiObject]:

    def _match(results: list[docspec.ApiObject]) -> t.Callable[[docspec.ApiObject], t.Any]:
      def matcher(obj: docspec.ApiObject) -> None:
        current_fqn = '.'.join(y.name for y in obj.path)
        if current_fqn == fqn:
          results.append(obj)
      return matcher

    results: list[docspec.ApiObject] = []
    docspec.visit(self._modules, _match(results))
    return results

  def __iter__(self) -> t.Iterator[docspec.Module]:
    return iter(self._modules)
