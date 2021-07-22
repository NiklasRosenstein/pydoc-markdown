
from abc import abstractproperty
import typing as t
import typing_extensions as te

import docspec
import docspec_python
from nr.stream import Stream

T = t.TypeVar('T')


def get_members_of_type(objs: t.Union[docspec.ApiObject, t.List[docspec.ApiObject]], type_: t.Type[T]) -> t.List[T]:
  if isinstance(objs, docspec.ApiObject):
    if hasattr(objs, 'members'):
      return [x for x in objs.members if isinstance(x, type_)]
    return []
  else:
    return Stream(get_members_of_type(x, type_) for x in objs).concat().collect()


def format_function_signature(func: docspec.Function, exclude_self: bool = False) -> bool:
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


def is_method(obj: docspec.ApiObject, reverse_map: docspec.ReverseMap) -> te.TypeGuard[docspec.Function]:
  return is_function(obj) and isinstance(reverse_map.get_parent(obj), docspec.Class)


def is_property(obj: docspec.ApiObject) -> te.TypeGuard[docspec.Function]:
  return is_function(obj) and any(d.name == 'property' for d in obj.decorations)


def is_attr(obj: docspec.ApiObject, reverse_map: docspec.ReverseMap) -> te.TypeGuard[docspec.Data]:
  return isinstance(obj, docspec.Data) and isinstance(reverse_map.get_parent(obj), docspec.Class)


def get_object_description(obj: docspec.ApiObject, reverse_map: docspec.ReverseMap = None) -> str:
  """
  Determines the best matching description of *obj*. Requires a #docspec.ReverseMap such that
  methods can be correclty identified as such. Returns a string such as "module", "class", "abstract class",
  "enum", "attribute", "property", "function", "method", "abstract method", "class method", "static method"
  and "abstract class method".
  """

  if isinstance(obj, docspec.Module):
    return 'module'
  elif isinstance(obj, docspec.Class):
    if any(x in (obj.bases or ()) for x in ('abc.ABC', 'ABC')) or \
       any(x in (obj.metaclass or ()) for x in ('abc.ABCMeta', 'ABCMeta')):
      return 'abstract class'
    return 'class'
  elif isinstance(obj, docspec.Function):
    if any(x.name == 'property' for x in obj.decorations):
      return 'property'
    if any(x.name in ('abc.abstractproperty', 'abstractproperty') for x in obj.decorations):
      return 'abstract property'
    if any(x.name in ('abc.abstractmethod', 'abstractmethod') for x in obj.decorations):
      return 'abstract method'
    if any(x.name in ('abc.abstractclassmethod', 'abstractclassmethod') for x in obj.decorations):
      return 'abstract class method'
    if any(x.name == 'classmethod' for x in obj.decorations):
      return 'class method'
    if any(x.name == 'staticmethod' for x in obj.decorations):
      return 'static method'
    if reverse_map and is_method(obj, reverse_map):
      return 'method'
    return 'function'
  elif isinstance(obj, docspec.Data):
    if reverse_map and is_attr(obj, reverse_map):
      return 'attribute'
    return 'data'
  else:
    assert False, type(obj)
