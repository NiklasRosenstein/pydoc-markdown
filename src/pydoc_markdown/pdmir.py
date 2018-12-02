
"""
This module implements the Pydoc-Markdown intermediate representation of
a package documentation suite.
"""


class Object(object):

  def __init__(self, name, docstring, filename, lineno):
    self.name = name
    self.members = {}
    self.parent = None
    self.docstring = docstring
    self.filename = filename
    self.lineno = lineno

  def __repr__(self):
    return '{0}(name={1.name}, filename={1.filename}, lineno={1.lineno})'\
      .format(type(self).__name__, self)

  def add_member(self, member):
    if not isinstance(member, Object):
      raise TypeError('expected Object, got {0}'.format(type(member).__name__))
    if member.parent:
      raise RuntimeError('member already has a parent')
    member.parent = self
    self.members[member.name] = member


class Namespace(Object):
  pass


class Function(Object):

  def __init__(self, name, docstring, args, filename, lineno):
    super(Function, self).__init__(name, docstring, filename, lineno)
    self.args = args  # list of FunctionArgument


class FunctionArgument(object):

  def __init__(self, name, annotation, default_value):
    self.name = name  # str
    self.annotation = annotation  # Expression
    self.default_value = default_value  # Expression


# class Expression(object):
#   pass
