
import os
import re
import textwrap

from .reflection import *
from lib2to3.refactor import RefactoringTool
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as syms
from lib2to3.pytree import Node


def parse_to_ast(code, filename):
  """
  Parses the string *code* to an AST with #lib2to3.
  """

  return RefactoringTool([]).refactor_string(code, filename)


def parse_file(code, filename, module_name=None):
  """
  Creates a reflection of the Python source in the string *code*.
  """

  return Parser().parse(parse_to_ast(code, filename), filename, module_name)


class Parser(object):

  def parse(self, ast, filename, module_name=None):
    self.filename = filename

    if module_name is None:
      module_name = os.path.basename(filename)
      module_name = os.path.splitext(filename)[0]

    docstring = None
    if ast.children:
      docstring = self.get_docstring_from_first_node(ast)

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

  def parse_statement(self, parent, stmt):
    is_assignment = False
    names = []
    expression = []
    for child in stmt.children:
      if child.value == '=':
        is_assignment = True
        names.append(expression)
        expression = []
      else:
        expression.append(child)
    if is_assignment:
      # TODO @NiklasRosenstein handle multiple assignments.
      docstring = self.get_statement_docstring(stmt)
      expr = Expression(self.nodes_to_string(expression))
      name = self.nodes_to_string(names[0])
      return Data(self.location_from(stmt), parent, name, docstring, expr=expr)
    return None

  def parse_decorator(self, node):
    assert node.children[0].value == '@'
    name = self.name_to_string(node.children[1])
    call_expr = self.nodes_to_string(node.children[2:]).strip()
    return Decorator(name, Expression(call_expr) if call_expr else None)

  def parse_funcdef(self, parent, node, is_async, decorators):
    parameters = next(x for x in node.children if x.type == syms.parameters)
    suite = next(x for x in node.children if x.type == syms.suite)

    name = node.children[1].value
    docstring = self.get_docstring_from_first_node(suite)
    args = []  # TODO @NiklasRosenstein parse function parameters
    return_ = None  # TODO @NiklasRosenstein parse function return annotation
    decorators = decorators or []

    return Function(self.location_from(node), parent, name, docstring,
      is_async=is_async, decorators=decorators, args=args, return_=return_)

  def parse_classdef(self, parent, node, decorators):
    name = node.children[1].value
    bases = []
    metaclass = None

    classargs = next((x for x in node.children if x.type == syms.arglist), None)
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

    suite = next(x for x in node.children if x.type == syms.suite)
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

  def get_docstring_from_first_node(self, parent):
    node = next((x for x in parent.children if isinstance(x, Node)), None)
    if not node:
      return None
    if node.type == syms.simple_stmt:
      if node.children[0].type == token.STRING:
        return self.prepare_docstring(node.children[0].value)
    return self.get_hashtag_docstring_from_prefix(node)

  def get_statement_docstring(self, node):
    ws = re.match('\s*', node.prefix[::-1]).group(0)
    if ws.count('\n') == 1:
      return self.get_hashtag_docstring_from_prefix(node)
    return None

  def get_hashtag_docstring_from_prefix(self, node):
    lines = []
    for line in reversed(node.prefix.split('\n')):
      line = line.strip()
      if lines and not line.startswith('#'): break
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
    elif s.startswith('"""') or s.startswith("'''"):
      return dedent_docstring(s[3:-3]).strip()
    elif s.startswith('"') or s.startswith("'"):
      return dedent_docstring(s[1:-1]).strip()

  def nodes_to_string(self, nodes):
    def generator():
      for i, node in enumerate(nodes):
        if i == 0:
          #yield node.prefix.rpartition('\n')[-1]
          pass
        else:
          yield node.prefix
        # TODO @NiklasRosenstein this might not work as expected if *node* is not a Leaf
        yield node.value
    return ''.join(generator())

  def name_to_string(self, node):
    if node.type == syms.dotted_name:
      return ''.join(x.value for x in node.children)
    else:
      return node.value


def dedent_docstring(s):
  lines = s.split('\n')
  lines[0] = lines[0].strip()
  lines[1:] = textwrap.dedent('\n'.join(lines[1:])).split('\n')
  return '\n'.join(lines)
