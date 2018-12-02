
import nr.types.named as named


class Location(named.Named):
  __annotations__ = [
    ('filename', str),
    ('lineno', int)
  ]


class Object(named.Named):
  __annotations__ = [
    ('location', str),
    ('parent', 'Object'),
    ('name', str),
    ('docstring', str),
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


class Data(Object):
  __annotations__ = [
    ('expr', 'Expression')
  ]


class Decorator(named.Named):
  __annotations__ = [
    ('name', str),
    ('args', 'Expression')
  ]


class Argument(named.Named):
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


class Expression(named.Named):
  __annotations__ = [
    ('text', str)
  ]


__all__ = ['Location', 'Module', 'Class', 'Function', 'Data', 'Decorator',
  'Argument', 'Expression']
