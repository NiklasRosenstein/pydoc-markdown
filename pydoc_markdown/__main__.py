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

import os, sys
import argparse
import textwrap

from . import write_module, import_module
from .markdown import MarkdownWriter

def main():
    parser = argparse.ArgumentParser(
        prog='pydoc-markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''
            Simple (ie. quick and dirty) script to generate a Markdown
            formatted help on a Python module. Contributions are welcome.

            Project Homepage:  https://github.com/NiklasRosenstein/pydoc-markdown
            ''')
    )
    parser.add_argument('module', help='name of the module to generate docs for')
    args = parser.parse_args()

    module = import_module(args.module)
    writer = MarkdownWriter(sys.stdout)
    write_module(writer, module)
    writer.close()


if __name__ == '__main__':
    main()
