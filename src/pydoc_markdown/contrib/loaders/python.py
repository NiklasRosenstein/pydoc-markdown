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
Loads Python source code into the Pydoc-markdown reflection format.
"""

import logging
import os
import pkgutil
import re
import textwrap
import sys

from lib2to3.refactor import RefactoringTool
from lib2to3.pgen2 import token
from lib2to3.pgen2.parse import ParseError
from lib2to3.pygram import python_symbols as syms
from lib2to3.pytree import Leaf, Node
from nr.databind.core import Field, Struct
from nr.interface import implements
from pydoc_markdown.interfaces import Loader, LoaderError
from pydoc_markdown.reflection import (
  Argument,
  Expression,
  Class,
  Data,
  Decorator,
  Function,
  Location,
  Module,
  ModuleGraph)

_REVERSE_SYMS = {v: k for k, v in vars(syms).items() if isinstance(v, int)}
_REVERSE_TOKEN = {v: k for k, v in vars(token).items() if isinstance(v, int)}

logger = logging.getLogger(__name__)


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


def parse_to_ast(code, filename, print_function=True):
  """
  Parses the string *code* to an AST with #lib2to3.
  """

  options = {'print_function': print_function}

  try:
    # NOTE (@NiklasRosenstein): Adding newline at the end as a ParseError
    #   could be raised without a trailing newline (tested in CPython 3.6
    #   and 3.7).
    return RefactoringTool([], options).refactor_string(code + '\n', filename)
  except ParseError as exc:
    raise ParseError(exc.msg, exc.type, exc.value, exc.context + (filename,))


def parse_file(code, filename, module_name=None, parser=None, **kwargs):
  """
  Creates a reflection of the Python source in the string *code*.
  """

  if code is None:
    with open(filename, 'r') as fp:
      code = fp.read()

  if parser is None:
    parser = Parser()

  return parser.parse(parse_to_ast(code, filename, **kwargs), filename, module_name)


class Parser:
  """
  A helper class that parses a Python AST to turn it into objects of the
  #pydoc_markdown.reflection module. Extracts docstrings from functions
  and single-line comments.
  """

  treat_singleline_comment_blocks_as_docstrings = True

  def parse(self, ast, filename, module_name=None):
    self.filename = filename  # pylint: disable=attribute-defined-outside-init

    if module_name is None:
      module_name = os.path.basename(filename)
      module_name = os.path.splitext(module_name)[0]

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

  def _split_statement(self, stmt):
    """
    Parses a statement node into three lists, consisting of the leaf nodes
    that are the name(s), annotation and value of the expression. The value
    list will be empty if this is not an assignment statement (but for example
    a plain expression).
    """

    def _parse(stack, current, stmt):
      for child in stmt.children:
        if not isinstance(child, Node) and child.value == '=':
          stack.append(current)
          current = ('value', [])
        elif not isinstance(child, Node) and child.value == ':':
          stack.append(current)
          current = ('annotation', [])
        elif isinstance(child, Node) and child.type == syms.annassign:
          _parse(stack, current, child)
        else:
          current[1].append(child)
      stack.append(current)
      return stack

    result = dict(_parse([], ('names', []), stmt))
    return result.get('names', []), result.get('annotation', []), result.get('value', [])

  def parse_statement(self, parent, stmt):
    names, annotation, value = self._split_statement(stmt)
    if value or annotation:
      docstring = self.get_statement_docstring(stmt)
      expr = Expression(self.nodes_to_string(value)) if value else None
      annotation = Expression(self.nodes_to_string(annotation)) if annotation else None
      assert names
      for name in names:
        name = self.nodes_to_string([name])
        data = Data(
          self.location_from(stmt),
          parent,
          name,
          docstring,
          expr=expr,
          annotation=annotation)
      return data
    return None

  def parse_decorator(self, node):
    assert node.children[0].value == '@'
    name = self.name_to_string(node.children[1])
    call_expr = self.nodes_to_string(node.children[2:]).strip()
    return Decorator(name, Expression(call_expr) if call_expr else None)

  def parse_funcdef(self, parent, node, is_async, decorators):
    parameters = find(lambda x: x.type == syms.parameters, node.children)
    body = find(lambda x: x.type == syms.suite, node.children) or \
      find(lambda x: x.type == syms.simple_stmt, node.children)

    name = node.children[1].value
    docstring = self.get_docstring_from_first_node(body)
    args = self.parse_parameters(parameters)
    return_ = self.get_return_annotation(node)
    decorators = decorators or []

    return Function(self.location_from(node), parent, name, docstring,
      is_async=is_async, decorators=decorators, args=args, return_=return_)

  def parse_argument(self, node, argtype, scanner):
    # type: (Union[Leaf, Node], str, ListScanner) -> Argument
    """
    Parses an argument from the AST. *node* must be the current node at
    the current position of the *scanner*. The scanner is used to extract
    the optional default argument value that follows the *node*.
    """

    def parse_annotated_name(node):
      if node.type == syms.tname:
        scanner = ListScanner(node.children)
        name = scanner.current.value
        node = scanner.advance()
        assert node.type == token.COLON, node.parent
        node = scanner.advance()
        annotation = Expression(self.nodes_to_string([node]))
      elif node:
        name = node.value
        annotation = None
      else:
        raise RuntimeError('unexpected node: {!r}'.format(node))
      return (name, annotation)

    name, annotation = parse_annotated_name(node)

    node = scanner.advance()
    default = None
    if node and node.type == token.EQUAL:
      node = scanner.advance()
      default = Expression(self.nodes_to_string([node]))
      node = scanner.advance()

    return Argument(name, annotation, default, argtype)

  def parse_parameters(self, parameters):
    assert parameters.type == syms.parameters, parameters.type
    result = []

    arglist = find(lambda x: x.type == syms.typedargslist, parameters.children)
    if not arglist:
      # NOTE (@NiklasRosenstein): A single argument (annotated or not) does
      #   not get wrapped in a `typedargslist`, but in a single `tname`.
      tname = find(lambda x: x.type == syms.tname, parameters.children)
      if tname:
        scanner = ListScanner(parameters.children, parameters.children.index(tname))
        result.append(self.parse_argument(tname, Argument.POS, scanner))
      else:
        assert len(parameters.children) in (2, 3), parameters.children
        if len(parameters.children) == 3:
          result.append(Argument(parameters.children[1].value, None, None, Argument.POS))
      return result

    argtype = Argument.POS

    index = ListScanner(arglist.children)
    for node in index.safe_iter(auto_advance=False):
      node = index.current
      if node.type == token.STAR:
        node = index.advance()
        if node.type == token.COMMA:
          result.append(Argument('', None, None, Argument.KW_SEPARATOR))
          index.advance()
        else:
          result.append(self.parse_argument(node, Argument.POS_REMAINDER, index))
          index.advance()
        argtype = Argument.KW_ONLY
        continue
      elif node.type == token.DOUBLESTAR:
        node = index.advance()
        result.append(self.parse_argument(node, Argument.KW_REMAINDER, index))
        continue
      result.append(self.parse_argument(node, argtype, index))
      index.advance()

    return result

  def parse_classdef_arglist(self, classargs):
    metaclass = None
    bases = []
    for child in classargs.children[::2]:
      if child.type == syms.argument:
        key, value = child.children[0].value, self.nodes_to_string(child.children[2:])
        if key == 'metaclass':
          metaclass = Expression(value)
        else:
          # TODO @NiklasRosenstein: handle metaclass arguments
          pass
      else:
        bases.append(Expression(str(child)))
    return metaclass, bases

  def parse_classdef_rawargs(self, classdef):
    metaclass = None
    bases = []
    index = ListScanner(classdef.children, 2)
    if index.current.type == token.LPAR:
      index.advance()
      while index.current.type != token.RPAR:
        if index.current.type == syms.argument:
          key = index.current.children[0].value
          value = Expression(str(index.current.children[2]))
          if key == 'metaclass':
            metaclass = value
          else:
            # TODO @NiklasRosenstein: handle metaclass arguments
            pass
        else:
          bases.append(Expression(str(index.current)))
        index.advance()
    return metaclass, bases

  def parse_classdef(self, parent, node, decorators):
    name = node.children[1].value
    bases = []
    metaclass = None

    # An arglist is available if there are at least two parameters.
    # Otherwise we have to deal with parsing a raw sequence of nodes.
    classargs = find(lambda x: x.type == syms.arglist, node.children)
    if classargs:
      metaclass, bases = self.parse_classdef_arglist(classargs)
    else:
      metaclass, bases = self.parse_classdef_rawargs(node)

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
    """
    This method retrieves the docstring for the block node *parent*. The
    node either declares a class or function.
    """

    node = find(lambda x: isinstance(x, Node), parent.children)
    if node and node.type == syms.simple_stmt:
      if node.children[0].type == token.STRING:
        return self.prepare_docstring(node.children[0].value)
    if not node and not module_level:
      return None
    if self.treat_singleline_comment_blocks_as_docstrings:
      docstring, doc_type = self.get_hashtag_docstring_from_prefix(node or parent)
      if doc_type == 'block':
        return docstring
    return None

  def get_statement_docstring(self, node):
    prefix = self.get_most_recent_prefix(node)
    ws = re.match(r'\s*', prefix[::-1]).group(0)
    if ws.count('\n') == 1:
      docstring, doc_type = self.get_hashtag_docstring_from_prefix(node)
      if doc_type == 'statement':
        return docstring
    # Look for the next string literal instead.
    while node and node.type != syms.simple_stmt:
      node = node.parent
    if node and node.next_sibling and node.next_sibling.type == syms.simple_stmt:
      string_literal = node.next_sibling.children[0]
      if string_literal.type == token.STRING:
        return self.prepare_docstring(string_literal.value)
    return None

  def get_hashtag_docstring_from_prefix(self, node):
    # type: (Node) -> (Optional[str], Optional[str])
    """
    Given a node in the AST, this method retrieves the docstring from the
    closest prefix of this node (ie. any block of single-line comments that
    precede this node).

    The function will also return the type of docstring: A docstring that
    begins with `#:` is a statement docstring, otherwise it is a block
    docstring (and only used for classes/methods).

    return: (docstring, doc_type)
    """

    prefix = self.get_most_recent_prefix(node)
    lines = []
    doc_type = None
    for line in reversed(prefix.split('\n')):
      line = line.strip()
      if lines and not line.startswith('#'):
        break
      if doc_type is None and line.strip().startswith('#:'):
        doc_type = 'statement'
      elif doc_type is None and line.strip().startswith('#'):
        doc_type = 'block'
      if lines or line:
        lines.append(line)
    return self.prepare_docstring('\n'.join(reversed(lines))), doc_type

  def prepare_docstring(self, s):
    # TODO @NiklasRosenstein handle u/f prefixes of string literal?
    s = s.strip()
    if s.startswith('#'):
      lines = []
      for line in s.split('\n'):
        line = line.strip()
        if line.startswith('#:'):
          line = line[2:]
        else:
          line = line[1:]
        lines.append(line.lstrip())
      return '\n'.join(lines).strip()
    if s.startswith('"""') or s.startswith("'''"):
      return dedent_docstring(s[3:-3]).strip()
    if s.startswith('"') or s.startswith("'"):
      return dedent_docstring(s[1:-1]).strip()
    return None

  def nodes_to_string(self, nodes):
    """
    Converts a list of AST nodes to a string.
    """

    def generator(nodes, skip_prefix=True):
      # type: (List[Node], Bool) -> Iterable[Tuple[str, str]]
      for i, node in enumerate(nodes):
        if not skip_prefix or i != 0:
          yield node.prefix
        if isinstance(node, Node):
          for _ in generator(node.children, True):
            yield _
        else:
          yield node.value

    return ''.join(generator(nodes))

  def name_to_string(self, node):
    if node.type == syms.dotted_name:
      return ''.join(x.value for x in node.children)
    else:
      return node.value


class ListScanner:
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
    to `True`, an #IndexError will be raised when there is no next element.
    Otherwise, `None` will be returned.
    """

    self._index += 1
    try:
      return self.current
    except IndexError:
      if expect:
        raise
      return None

  def safe_iter(self, auto_advance=True):
    """
    A useful generator function that iterates over every element in the list.
    You may call #advance() during the iteration to retrieve the next
    element in the list within a single iteration.

    If *auto_advance* is `True` (default), the function generator will
    always advance to the next element automatically. If it is set to `False`,
    #advance() must be called manually in every iteration to ensure that
    the scanner has advanced at least to the next element, or a
    #RuntimeError will be raised.
    """

    index = self._index
    while self:
      yield self.current
      if auto_advance:
        self.advance()
      elif self._index == index:
        raise RuntimeError('next() has not been called on the ListScanner')


@implements(Loader)
class PythonLoader(Struct):
  """
  This implementation of the #Loader interface parses Python modules and
  packages. Which files are parsed depends on the configuration (see
  #PythonLoaderConfig).

  If no #modules or #packages are set, the loader will attempt to find
  # packages in the src/ folder of the current directory.
  """

  #: A list of module names that this loader will search for and then parse.
  #: The modules are searched using the #sys.path of the current Python
  # interpreter, unless the #search_path option is specified.
  modules = Field([str], default=None)

  #: A list of package names that this loader will search for and then parse,
  #: including all sub-packages and modules.
  packages = Field([str], default=None)

  #: The module search path. If not specified, the current #sys.path is
  #: used instead. If any of the elements contain a `*` (star) symbol, it
  #: will be expanded with #sys.path.
  search_path = Field([str], default=None)

  #: The "print_function" flag will be passed down to the lib2to3
  #: RefactoringTool. This enables parsing Python 3 code that uses the
  #: print function without importing the print_function from the
  #: `__future__` module.
  print_function = Field(bool, default=True)

  #: Whether to treat blocks of single line comments as docstrings at the
  #: header of a module or inside a class or function definition. Defaults to True.
  treat_singleline_comment_blocks_as_docstrings = Field(bool, default=True)

  IGNORE_DISCOVERED_MODULES = ('test', 'tests', 'setup')

  def load(self, graph):
    if self.search_path is None:
      search_path = ['.', 'src'] if self.modules is None else sys.path
    else:
      search_path = list(self.search_path)
      if '*' in search_path:
        index = search_path.index('*')
        search_path[index:index+1] = sys.path

    if self.modules is None and self.packages is None:
      modules = []
      packages = []
      for path in search_path:
        try:
          items = os.listdir(path)
        except OSError:
          continue
        for name in items:
          if name.endswith('.py') and name[:-3] not in self.IGNORE_DISCOVERED_MODULES:
            modules.append(name[:-3])
            continue
          full_path = os.path.join(path, name, '__init__.py')
          if os.path.isfile(full_path) and name not in self.IGNORE_DISCOVERED_MODULES:
            packages.append(name)
      if not modules and not packages:
        logger.warning('No Python modules or packages detected.')
      else:
        logger.info('Detected packages in search_path: %s', packages)
    else:
      modules = self.modules or []
      packages = self.packages or []

    old_path = sys.path
    sys.path = search_path
    try:
      for module in modules:
        self._load_module(graph, module, False)
      for package in packages:
        self._load_module(graph, package, True)
    finally:
      sys.path = old_path

  def _load_module(self, graph: ModuleGraph, module_name: str, recursive: bool) -> None:
    try:
      loader = pkgutil.find_loader(module_name)
      if loader is None:
        raise LoaderError('module "{}" not found'.format(module_name))
      path = loader.get_filename()
    except ImportError as exc:
      raise LoaderError(exc)

    if recursive:
      if os.path.basename(path).startswith('__init__.'):
        path = os.path.dirname(path)
      for submodule_name, filename in self._iter_module_files(module_name, path):
        module = self.load_file(submodule_name, filename)
        graph.add_module(module)
    else:
      module = self.load_file(module_name, path)
      graph.add_module(module)

  def _iter_module_files(self, module_name, path):
    # pylint: disable=stop-iteration-return
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

  def _get_parser(self):
    parser = Parser()
    parser.treat_singleline_comment_blocks_as_docstrings = self.treat_singleline_comment_blocks_as_docstrings
    return parser

  def load_file(self, module_name, filename):
    return parse_file(
      None,
      filename,
      module_name,
      parser=self._get_parser(),
      print_function=self.print_function)

  def load_source(self, source_code, module_name, filename=None):
    ast = parse_to_ast(
      source_code,
      filename,
      print_function=self.print_function)
    return self._get_parser().parse(ast, filename, module_name)
