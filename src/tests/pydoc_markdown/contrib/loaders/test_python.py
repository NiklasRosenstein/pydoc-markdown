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

import pytest
import textwrap

from pydoc_markdown.reflection import Argument, Expression, Function
from pydoc_markdown.contrib.loaders.python import parse_file


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
    def assert_(module, docstring):
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
    assert_(module, None)

    module = self.parse('''
      def func(self):
        # ABC
        #   DEF
        return self.foo
    ''')
    assert_(module, 'ABC\nDEF')

    module = self.parse('''
      def func(self):
        """ ABC
          DEF """
        return self.foo
    ''')
    assert_(module, 'ABC\nDEF')

    module = self.parse('''
      def func(self):
        """
        ABC
          DEF
        """
        return self.foo
    ''')
    assert_(module, 'ABC\n  DEF')
