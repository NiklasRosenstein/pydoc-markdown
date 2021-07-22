
import typing as t

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


def is_method(obj: docspec.ApiObject, reverse_map: docspec.ReverseMap) -> bool:
  return isinstance(obj, docspec.Function) and isinstance(reverse_map.get_parent(obj), docspec.Class)
