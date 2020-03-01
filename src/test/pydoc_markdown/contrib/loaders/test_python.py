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

from pydoc_markdown.reflection import Argument, Expression, Function
from pydoc_markdown.contrib.loaders.python import parse_file
import textwrap


class TestParser:

  def setup_method(self, test_method):
    self.current_test_method = test_method

  def parse(self, code):
    return parse_file(textwrap.dedent(code), self.current_test_method.__name__)

  def test_parser_function_def(self):
    module = self.parse('''
      def fun(project_name, project_type, port=8001):
        pass
    ''')
    assert module.name == 'test_parser_function_def'
    assert len(module.members) == 1

    fun = module.members['fun']
    assert type(fun) is Function
    assert fun.name == 'fun'
    assert len(fun.args) == 3
    assert fun.args == [
      Argument('project_name', None, None, Argument.POS),
      Argument('project_type', None, None, Argument.POS),
      Argument('port', None, Expression('8001'), Argument.POS),
    ]
    assert fun.return_ is None

  def test_parser_function_def_annotations(self):
    module = self.parse('''
      def fun(project_name: str, project_type: ProjectType, port: int=8001) -> bool:
        pass
    ''')

    assert module.name == 'test_parser_function_def_annotations'
    assert len(module.members) == 1

    fun = module.members['fun']
    assert type(fun) is Function
    assert fun.name == 'fun'
    assert len(fun.args) == 3
    assert fun.args == [
      Argument('project_name', Expression('str'), None, Argument.POS),
      Argument('project_type', Expression('ProjectType'), None, Argument.POS),
      Argument('port', Expression('int'), Expression('8001'), Argument.POS),
    ]
    assert fun.return_ == Expression('bool')

  def test_parser_function_single_stmt(self):
    def assert_funcdef(module, docstring):
      assert module.name == 'test_parser_function_single_stmt'
      assert len(module.members) == 1

      func = module.members['func']
      assert type(func) is Function
      assert func.name == 'func'
      assert len(func.args) == 1
      assert func.args == [Argument('self', None, None, Argument.POS)]
      assert func.return_ is None
      assert func.docstring == docstring

    module = self.parse('''
      def func(self): return self.foo
    ''')
    assert_funcdef(module, None)

    module = self.parse('''
      def func(self):
        # ABC
        #   DEF
        return self.foo
    ''')
    assert_funcdef(module, 'ABC\nDEF')

    module = self.parse('''
      def func(self):
        """ ABC
          DEF """
        return self.foo
    ''')
    assert_funcdef(module, 'ABC\nDEF')

    module = self.parse('''
      def func(self):
        """
        ABC
          DEF
        """
        return self.foo
    ''')
    assert_funcdef(module, 'ABC\n  DEF')

  def test_parser_function_starred_args(self):
    def assert_funcdef(module, arglist):
      func = module.members['func']
      assert func.args == arglist

    module = self.parse('''
      def func(a, *, b, **c): pass
    ''')
    assert_funcdef(module, [
      Argument('a', None, None, Argument.POS),
      Argument('', None, None, Argument.KW_SEPARATOR),
      Argument('b', None, None, Argument.KW_ONLY),
      Argument('c', None, None, Argument.KW_REMAINDER)
    ])
    assert module.members['func'].signature == 'func(a, *, b, **c)'

    module = self.parse('''
      def func(*args, **kwargs):
        """ Docstring goes here. """
    ''')
    assert_funcdef(module, [
      Argument('args', None, None, Argument.POS_REMAINDER),
      Argument('kwargs', None, None, Argument.KW_REMAINDER),
    ])
    assert module.members['func'].signature == 'func(*args, **kwargs)'

    module = self.parse('''
      def func(*, **kwargs):
        """ Docstring goes here. """
    ''')
    assert_funcdef(module, [
      Argument('', None, None, Argument.KW_SEPARATOR),
      Argument('kwargs', None, None, Argument.KW_REMAINDER),
    ])
    assert module.members['func'].signature == 'func(*, **kwargs)'

    module = self.parse('''
      def func(abc, *,):
          """Docstring goes here."""
    ''')
    assert_funcdef(module, [
      Argument('abc', None, None, Argument.POS),
      Argument('', None, None, Argument.KW_SEPARATOR),
    ])
    assert module.members['func'].signature == 'func(abc, *)'

  def test_parser_class_bases(self):
    module = self.parse('''
      class MyError:
        pass
    ''')
    assert module.members['MyError'].bases == []
    assert module.members['MyError'].metaclass is None

    module = self.parse('''
      class MyError():
        pass
    ''')
    assert module.members['MyError'].bases == []
    assert module.members['MyError'].metaclass is None

    module = self.parse('''
      class MyError(RuntimeError):
        pass
    ''')
    assert module.members['MyError'].bases == [Expression('RuntimeError')]
    assert module.members['MyError'].metaclass is None

    module = self.parse('''
      class MyError(RuntimeError, metaclass=ABCMeta):
        pass
    ''')
    assert module.members['MyError'].bases == [Expression('RuntimeError')]
    assert module.members['MyError'].metaclass == Expression('ABCMeta')

    module = self.parse('''
      class MyError(metaclass=ABCMeta):
        pass
    ''')
    assert module.members['MyError'].bases == []
    assert module.members['MyError'].metaclass == Expression('ABCMeta')
