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

import re

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
