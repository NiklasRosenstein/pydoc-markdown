
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
    prefix = self.name
    if self.is_method():
      prefix = self.parent.name + '.' + prefix
    return '{}({})'.format(prefix, Argument.format_arglist(self.args))


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
    return ' '.join(parts)


class Expression(named.Named):
  __annotations__ = [
    ('text', str)
  ]

  def __str__(self):
    return self.text


__all__ = ['Location', 'Module', 'Class', 'Function', 'Data', 'Decorator',
  'Argument', 'Expression']
