
import imp
import os
import re
import textwrap
import sys

from lib2to3.refactor import RefactoringTool
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as syms
from lib2to3.pytree import Node
from nr.types.structured import Field, Object
from nr.types.interface import implements
from pydoc_markdown.interfaces import Loader, LoaderError
from pydoc_markdown.reflection import *


def dedent_docstring(s):
  lines = s.split('\n')
  lines[0] = lines[0].strip()
  lines[1:] = textwrap.dedent('\n'.join(lines[1:])).split('\n')
  return '\n'.join(lines).strip()


def find(predicate, iterable):
  for item in iterable:
    if predicate(item):
      return item
  return None


def parse_to_ast(code, filename):
  """
  Parses the string *code* to an AST with #lib2to3.
  """

  return RefactoringTool([]).refactor_string(code, filename)


def parse_file(code, filename, module_name=None):
  """
  Creates a reflection of the Python source in the string *code*.
  """

  if code is None:
    with open(filename, 'r') as fp:
      code = fp.read()

  return Parser().parse(parse_to_ast(code, filename), filename, module_name)


class Parser(object):
  """
  A helper class that parses a Python AST to turn it into objects of the
  [[pydoc_markdown.reflection]] module. Extracts docstrings from functions
  and single-line comments.
  """

  def parse(self, ast, filename, module_name=None):
    self.filename = filename

    if module_name is None:
      module_name = os.path.basename(filename)
      module_name = os.path.splitext(module_name)[0]

    docstring = None
    if ast.children:
      docstring = self.get_docstring_from_first_node(ast, module_level=True)

    module = Module(self.location_from(ast), None, module_name, docstring)

    for node in ast.children:
      self.parse_declaration(module, node)

    return module

  def parse_declaration(self, parent, node, decorators=None):
    if node.type == syms.simple_stmt:
      assert not decorators
      stmt = node.children[0]
      if stmt.type in (syms.import_name, syms.import_from):
        # TODO @NiklasRosenstein handle import statements?
        pass
      elif stmt.type == syms.expr_stmt:
        return self.parse_statement(parent, stmt)
    elif node.type == syms.funcdef:
      return self.parse_funcdef(parent, node, False, decorators)
    elif node.type == syms.classdef:
      return self.parse_classdef(parent, node, decorators)
    elif node.type in (syms.async_stmt, syms.async_funcdef):
      child = node.children[1]
      if child.type == syms.funcdef:
        return self.parse_funcdef(parent, child, True, decorators)
    elif node.type == syms.decorated:
      assert len(node.children) == 2
      decorators = []
      if node.children[0].type == syms.decorator:
        decorator_nodes = [node.children[0]]
      elif node.children[0].type == syms.decorators:
        decorator_nodes = node.children[0].children
      else:
        assert False, node.children[0].type
      for child in decorator_nodes:
        assert child.type == syms.decorator, child.type
        decorators.append(self.parse_decorator(child))
      return self.parse_declaration(parent, node.children[1], decorators)
    return None

  def parse_statement(self, parent, stmt):
    is_assignment = False
    names = []
    expression = []
    for child in stmt.children:
      if not isinstance(child, Node) and child.value == '=':
        is_assignment = True
        names.append(expression)
        expression = []
      else:
        expression.append(child)
    if is_assignment:
      docstring = self.get_statement_docstring(stmt)
      expr = Expression(self.nodes_to_string(expression))
      assert names
      for name in names:
        name = self.nodes_to_string(name)
        data = Data(self.location_from(stmt), parent, name, docstring, expr=expr)
      return data
    return None

  def parse_decorator(self, node):
    assert node.children[0].value == '@'
    name = self.name_to_string(node.children[1])
    call_expr = self.nodes_to_string(node.children[2:]).strip()
    return Decorator(name, Expression(call_expr) if call_expr else None)

  def parse_funcdef(self, parent, node, is_async, decorators):
    parameters = find(lambda x: x.type == syms.parameters, node.children)
    suite = find(lambda x: x.type == syms.suite, node.children)

    name = node.children[1].value
    docstring = self.get_docstring_from_first_node(suite)
    args = self.parse_parameters(parameters)
    return_ = self.get_return_annotation(node)
    decorators = decorators or []

    return Function(self.location_from(node), parent, name, docstring,
      is_async=is_async, decorators=decorators, args=args, return_=return_)

  def parse_parameters(self, parameters):
    assert parameters.type == syms.parameters, parameters.type
    result = []

    arglist = find(lambda x: x.type == syms.typedargslist, parameters.children)
    if not arglist:
      assert len(parameters.children) in (2, 3), parameters.children
      if len(parameters.children) == 3:
        result.append(Argument(parameters.children[1].value, None, None, Argument.POS))
      return result

    def consume_arg(node, argtype, index):
      if node.type == syms.tname:
        index = ListScanner(node.children)
      name = node.value
      node = index.advance()
      annotation = None
      if node and node.type == token.COLON:
        node = index.advance()
        annotation = Expression(self.nodes_to_string([node]))
        node = index.advance()
      default = None
      if node and node.type == token.EQUAL:
        node = index.advance()
        default = Expression(self.nodes_to_string([node]))
        node = index.advance()
      return Argument(name, annotation, default, argtype)

    argtype = Argument.POS

    index = ListScanner(arglist.children)
    for node in index.safe_iter():
      node = index.current
      if node.type == token.STAR:
        node = index.advance()
        if node.type != token.COMMA:
          result.append(consume_arg(node, Argument.POS_REMAINDER, index))
        else:
          index.advance()
        argtype = Argument.KW_ONLY
        continue
      elif node.type == token.DOUBLESTAR:
        node = index.advance()
        result.append(consume_arg(node, Argument.KW_REMAINDER, index))
        continue
      result.append(consume_arg(node, argtype, index))
      index.advance()

    return result

  def parse_classdef(self, parent, node, decorators):
    name = node.children[1].value
    bases = []
    metaclass = None

    classargs = find(lambda x: x.type == syms.arglist, node.children)
    if classargs:
      for child in classargs.children[::2]:
        if child.type == syms.argument:
          key, value = child.children[0].value, self.nodes_to_string(child.children[2:])
          if key == 'metaclass':
            metaclass = Expression(value)
          else:
            # TODO @NiklasRosenstein handle metaclass arguments
            pass
        else:
          bases.append(Expression(str(child)))

    suite = find(lambda x: x.type == syms.suite, node.children)
    docstring = self.get_docstring_from_first_node(suite)
    class_ = Class(self.location_from(node), parent, name, docstring,
      bases=bases, metaclass=metaclass, decorators=decorators)

    for child in suite.children:
      if isinstance(child, Node):
        member = self.parse_declaration(class_, child)
        if metaclass is None and isinstance(member, Data) and \
            member.name == '__metaclass__':
          metaclass = member.expr
          member.remove()

    return class_

  def location_from(self, node):
    return Location(self.filename, node.get_lineno())

  def get_return_annotation(self, node):
    rarrow = find(lambda x: x.type == token.RARROW, node.children)
    if rarrow:
      node = rarrow.next_sibling
      return Expression(self.nodes_to_string([node]))
    return None

  def get_most_recent_prefix(self, node):
    if node.prefix:
      return node.prefix
    while not node.prev_sibling and not node.prefix:
      if not node.parent:
        return ''
      node = node.parent
    if node.prefix:
      return node.prefix
    node = node.prev_sibling
    while isinstance(node, Node) and node.children:
      node = node.children[-1]
    return node.prefix

  def get_docstring_from_first_node(self, parent, module_level=False):
    node = find(lambda x: isinstance(x, Node), parent.children)
    if not node:
      return None
    if node.type == syms.simple_stmt:
      if node.children[0].type == token.STRING:
        return self.prepare_docstring(node.children[0].value)
    return self.get_hashtag_docstring_from_prefix(node)

  def get_statement_docstring(self, node):
    prefix = self.get_most_recent_prefix(node)
    ws = re.match('\s*', prefix[::-1]).group(0)
    if ws.count('\n') == 1:
      return self.get_hashtag_docstring_from_prefix(node)
    return None

  def get_hashtag_docstring_from_prefix(self, node):
    prefix = self.get_most_recent_prefix(node)
    lines = []
    for line in reversed(prefix.split('\n')):
      line = line.strip()
      if lines and not line.startswith('#'):
        break
      if lines or line:
        lines.append(line)
    return self.prepare_docstring('\n'.join(reversed(lines)))

  def prepare_docstring(self, s):
    # TODO @NiklasRosenstein handle u/f prefixes of string literal?
    s = s.strip()
    if s.startswith('#'):
      lines = []
      for line in s.split('\n'):
        lines.append(line.strip()[1:].lstrip())
      return '\n'.join(lines).strip()
    if s.startswith('"""') or s.startswith("'''"):
      return dedent_docstring(s[3:-3]).strip()
    if s.startswith('"') or s.startswith("'"):
      return dedent_docstring(s[1:-1]).strip()
    return None

  def nodes_to_string(self, nodes):
    def generator(nodes, skip_prefix=True):
      for i, node in enumerate(nodes):
        if not skip_prefix or i != 0:
          yield node.prefix
        if isinstance(node, Node):
          for _ in generator(node.children, i == 0):
            yield _
        else:
          yield node.value
    return ''.join(generator(nodes))

  def name_to_string(self, node):
    if node.type == syms.dotted_name:
      return ''.join(x.value for x in node.children)
    else:
      return node.value


class ListScanner(object):
  """
  A helper class to navigate through a list. This is useful if you would
  usually iterate over the list by index to be able to acces the next
  element during the iteration.

  Example:

  ```py
  scanner = ListScanner(lst)
  for value in scanner.safe_iter():
    if some_condition(value):
      value = scanner.advance()
  ```
  """

  def __init__(self, lst, index=0):
    self._list = lst
    self._index = index

  def __bool__(self):
    return self._index < len(self._list)

  __nonzero__ = __bool__

  @property
  def current(self):
    """
    Returns the current list element.
    """

    return self._list[self._index]

  def can_advance(self):
    """
    Returns `True` if there is a next element in the list.
    """

    return self._index < (len(self._list) - 1)

  def advance(self, expect=False):
    """
    Advances the scanner to the next element in the list. If *expect* is set
    to `True`, an [[IndexError]] will be raised when there is no next element.
    Otherwise, `None` will be returned.
    """

    self._index += 1
    try:
      return self.current
    except IndexError:
      if expect: raise
      return None

  def safe_iter(self, auto_advance=True):
    """
    A useful generator function that iterates over every element in the list.
    You may call [[advance()]] during the iteration to retrieve the next
    element in the list within a single iteration.

    If *auto_advance* is `True` (default), the function generator will
    always advance to the next element automatically. If it is set to `False`,
    [[advance()]] must be called manually in every iteration to ensure that
    the scanner has advanced at least to the next element, or a
    [[RuntimeError]] will be raised.
    """

    index = self._index
    while self:
      yield self.current
      if auto_advance:
        self.advance()
      elif self._index == index:
        raise RuntimeError('next() has not been called on the ListScanner')


class PythonLoaderConfig(Object):
  #: A list of module or package names that this loader will search for and
  #: then parse. The modules are searched using the [[sys.path]] of the current
  #: Python interpreter, unless the [[search_path]] option is specified.
  modules = Field([str])

  #: The module search path. If not specified, the current [[sys.path]] is
  #: used instead. If any of the elements contain a `*` (star) symbol, it
  #: will be expanded with [[sys.path]].
  search_path = Field([str], default=None)


@implements(Loader)
class PythonLoader(object):
  """
  This implementation of the [[Loader]] interface parses Python modules and
  packages. Which files are parsed depends on the configuration (see
  [[PythonLoaderConfig]]).
  """

  def get_config_class(self):
    return PythonLoaderConfig

  def load(self, config, graph):
    path = config.search_path
    if path is None:
      path = sys.path
    elif '*' in path:
      index = path.index('*')
      path[index:index+1] = sys.path

    for module in config.modules:
      try:
        path = imp.find_module(module, path)[1]
      except ImportError as exc:
        raise LoaderError(exc)
      for module_name, filename in self._iter_module_files(module, path):
        module = parse_file(None, filename, module_name)
        graph.add_module(module)

  def _iter_module_files(self, module_name, path):
    if os.path.isfile(path):
      yield module_name, path
      return
    elif os.path.isdir(path):
      yield next(self._iter_module_files(module_name, os.path.join(path, '__init__.py')))
      for item in os.listdir(path):
        if item == '__init__.py':
          continue
        item_abs = os.path.join(path, item)
        name = module_name + '.' + item.rstrip('.py')
        if os.path.isdir(item_abs) and os.path.isfile(os.path.join(item_abs, '__init__.py')):
          for x in self._iter_module_files(name, item_abs):
            yield x
        elif os.path.isfile(item_abs) and item_abs.endswith('.py'):
          yield next(self._iter_module_files(name, item_abs))
      return
    else:
      raise LoaderError('path "{}" does not exist'.format(path))
