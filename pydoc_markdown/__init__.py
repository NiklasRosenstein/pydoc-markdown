# Copyright (C) 2016  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function

__version__ = '0.1.0'
__author__ = 'Niklas Rosenstein <rosensteinniklas(at)gmail.com>'


import inspect
import sys
import textwrap
import types

Py3 = sys.version_info[0] == 3
class_types = (type,) if Py3 else (types.TypeType, types.ClassType)
integer_types = int if Py3 else (long, int)
string_types = (str,) if Py3 else (basestring,)
text_type = str if Py3 else unicode
binary_type = bytes if Py3 else str
function_types = (types.FunctionType, types.LambdaType, types.BuiltinFunctionType)
method_types = (types.MethodType, types.BuiltinMethodType)

special_member_types = (property, staticmethod, classmethod)
special_names = frozenset([
    '__name__', '__doc__', '__dict__', '__module__', '__weakref__'])


def argspec_format(func):
    '''
    Uses the :mod:`inspect` module to generate the argument specs of
    the specified function and returns it including parantheses.

    Args:
        func (function): The function to get the argument specs for.
    Raises:
        TypeError: If *func* is not a function.
    '''

    if not isinstance(func, function_types + method_types):
        raise TypeError('func is not a function', type(func))
    try:
        return inspect.formatargspec(*inspect.getargspec(func))
    except TypeError:
        return '(...)'


def import_module(module_name):
    '''
    Imports the specified module by name.
    '''

    parts = module_name.split('.')
    module = __import__(module_name)
    for part in parts[1:]:
        module = getattr(module, part)
    return module


def write_docstring(md, doc):
    '''
    Writes the specified Python *docstring* to the markdown writer.
    '''

    if not doc:
        md.newline()
        return

    doc = textwrap.dedent(doc).strip()
    md.blockquote(doc)
    md.newline()


def write_function(md, func, name, prefix=None):
    # Built-in functions often have the function name and
    # arg specs on the first line. We'll use that if it is
    # preset.
    doc = textwrap.dedent(func.__doc__ or '').strip()
    if doc.startswith(name):
        parts = doc.split('\n', 1)
        name = parts[0].strip()
        doc = parts[1] if len(parts) > 1 else None
    else:
        name = name + argspec_format(func)

    write_member(md, name, prefix)
    write_docstring(md, doc)


def write_class(md, cls, name=None):
    name = cls.__module__ + '.' + (name or cls.__name__)
    md.header('{0} Objects\n'.format(name))
    md.newline()
    md.push_header(2)

    special = []
    other = []

    for attr in sorted(vars(cls)):
        if attr.startswith('__') and attr.endswith('__'):
            if attr not in special_names:
                special.append(attr)
        elif not attr.startswith('_'):
            other.append(attr)

    for attr in (special + other):
        write_class_member(md, getattr(cls, attr), attr)

    md.pop_header()


def write_class_member(md, value, name):
    # Determine if the value is a special value (property, static- or
    # classmethod or abstract).
    prefix = ''
    for tpe in special_member_types:
        if isinstance(value, tpe):
            prefix = type_.__name__
            break
    if hasattr(value, '__isabstractmethod__'):
        prefix = ('abstract ' + prefix).strip()

    if isinstance(value, function_types + method_types):
        write_function(md, value, name, prefix)
    elif value is None:
        write_member(md, name + ' = None', prefix)
    else:
        write_member(md, name, prefix)


def write_member(md, member, prefix=None):
    md.header_level.append(5)
    md.header()
    md.pop_header()
    if prefix:
        md.code(prefix, italic=True)
    md.code(member)
    md.newline()
    md.newline()


def write_module(md, module, recursive=True):
    '''
    Formats the specified Python module and its contents into markdown
    syntax using the :class:`MarkdownWriter` *md*. If *recursive* is
    specified, all sub-packages and -modules will be included.
    '''

    if isinstance(module, str):
        module = import_module(module)

    md.header('{0} Module'.format(module.__name__))
    write_docstring(md, module.__doc__)

    # Collect a list of all data, functions and classes in the
    # module so we can put them into sections.
    data = []
    functions = []
    classes = []

    for attr in dir(module):
        if attr.startswith('_'):
            continue
        value = getattr(module, attr)
        from_module = getattr(value, '__module__', None)
        if from_module is not None and from_module != module.__name__:
            continue
        if isinstance(value, class_types):
            classes.append(attr)
        elif isinstance(value, function_types):
            functions.append(attr)
        elif not isinstance(value, types.ModuleType):
            data.append(attr)

    md.push_header(1)

    if data:
        md.header('Data')
    for attr in data:
        value = repr(getattr(module, attr))
        if len(value) > 23:
            value = value[:20] + '...'
        md.ul_item()
        md.code('{0} = {1}'.format(attr, value))
        md.newline()

    if functions:
        md.header('Functions')
    for attr in functions:
        value = getattr(module, attr)
        write_function(md, value, name=attr)
    for attr in classes:
        value = getattr(module, attr)
        write_class(md, value, name=attr)

    md.pop_header()

    if recursive:
        for name in sorted(sys.modules):
            value = sys.modules[name]
            if value and name.startswith(module.__name__ + '.'):
                write_module(md, sys.modules[name])
