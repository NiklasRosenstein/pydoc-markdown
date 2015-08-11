# Copyright (C) 2015 Niklas Rosenstein
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
"""
Simple script to get a Markdown formatted documentation for a Python
module or package.
"""

from __future__ import print_function

import inspect
import re
import sys
import textwrap
import types

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '0.1.0'


Py3 = sys.version_info[0] == 3
class_types = (type,) if Py3 else (types.TypeType, types.ClassType)
integer_types = int if Py3 else (long, int)
string_types = (str,) if Py3 else (basestring,)
text_type = str if Py3 else unicode
binary_type = bytes if Py3 else str
function_types = (types.FunctionType, types.LambdaType, types.BuiltinFunctionType)
method_types = (types.MethodType, types.BuiltinMethodType)

special_member_types = (property, staticmethod, classmethod)
special_names = frozenset(('__name__', '__doc__', '__dict__', '__module__',
    '__weakref__'))


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

    md.header_level.append(5)
    md.header()
    md.pop_header()
    if prefix:
        md.code(prefix, italic=True)
    md.code(name)
    md.newline()
    md.newline()

    write_docstring(md, doc)


def write_class(md, cls, name=None):
    name = cls.__module__ + (name or cls.__name__)
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

    if isinstance(value, types.MethodType):
        write_function(md, value, name, prefix)
    else:
        if prefix:
            md.code(prefix)
        md.code(name, bold=True)
        md.newline()


def write_member(md, member, prefix=None):
    if prefix:
        md.code(prefix)
    md.code(member, bold=True)
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
        if attr.startswith('__'):
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


class MarkdownWriter(object):
    '''
    Simple helper to write markdown text.
    '''

    def __init__(self, fp):
        super(MarkdownWriter, self).__init__()
        self.fp = fp
        self.header_level = []
        self.links = {}

    def push_header(self, level_increase=1):
        if self.header_level:
            level_increase += self.header_level[-1]
        else:
            level_increase += 1
        self.header_level.append(level_increase)

    def pop_header(self):
        self.header_level.pop()

    def header(self, text=None):
        '''
        Begins a markdown header with the appropriate depth. Use
        :meth:`push_header` and :meth:`pop_header` to change the
        header indentation level.
        '''

        level = 1
        if self.header_level:
            level = self.header_level[-1]
        self.fp.write('\n' + '#' * level + ' ')
        if text:
            self.fp.write(text)
            self.fp.write('\n')

    def newline(self):
        '''
        Writes a newline to the file.
        '''

        self.fp.write('\n')

    def text(self, text):
        '''
        Writes *text* to the file.
        '''

        self.fp.write(text)
        if not text.endswith('\n') or not text.endswith(' '):
            self.fp.write(' ')

    def blockquote(self, text):
        for line in text.rstrip().split('\n'):
            self.fp.write('> ')
            self.fp.write(line)
            if not line.endswith('\n'):
                self.fp.write('\n')
        self.fp.write('\n')

    def code_block(self, code, language=None):
        '''
        Writes *code* as a code-block to the code. If *language* is
        not specified, the code will be written as an indented code
        block, otherwise the triple code block formatting is used.
        You should make sure the code block is preceeded by a newline.
        '''

        code = textwrap.dedent(code).strip()
        if language:
            self.fp.write('```{0}\n'.format(language))
            self.fp.write(code)
            self.fp.write('```\n')
        else:
            for line in code.split():
                self.fp.write('    ')
                self.fp.write(line)
            self.fp.write('\n')

    def code(self, text, italic=False, bold=False):
        '''
        Encloses *text* in backticks.
        '''

        # To escape backticks in *text*, we need more initial backticks
        # than contained in the text.
        # todo: this can probably be solved more efficent.
        matches = re.findall(r'(?<!\\)`+', text)
        if matches:
            backticks = max(len(x) for x in matches) + 1
        else:
            backticks = 1
        if italic:
            self.fp.write('*')
        if bold:
            self.fp.write('__')
        self.fp.write('`' * backticks)
        self.fp.write(text)
        if text.endswith('`'):
            self.fp.write(' ')
        self.fp.write('`' * backticks)
        if bold:
            self.fp.write('__')
        if italic:
            self.fp.write('*')
        self.fp.write(' ')

    def link(self, text, alias=None, url=None):
        '''
        Writes a link into the markdown file. If only *text* is
        specified, the alias will be the *text* itself. If an *url*
        is passed, an inline link will be generated. Conflicts with
        providing the *alias* option.
        '''

        if alias and url:
            raise ValueError('conflicting arguments alias and url')

        text = text.replace('[', '\[').replace(']', '\]')
        self.fp.write(text)
        if url:
            self.fp.write('({0}) '.format(self.url))
        elif alias:
            self.fp.write('[{0}] '.format(self.alias))
        else:
            self.fp.write('[] ')

    def ul_item(self):
        self.fp.write('- ')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('module')
    args = parser.parse_args()

    try:
        module = import_module(args.module)
    except ImportError as exc:
        print(exc, file=sys.stderr)

    writer = MarkdownWriter(sys.stdout)
    write_module(writer, module)


if __name__ == '__main__':
    main()
