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

import sys
import os
import argparse

from .pydoc_markdown import write_module, import_module
from .markdown_writer import MarkdownWriter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('module')
    args = parser.parse_args()
    module = None

    try:
        # Add current working dir to module search path
        sys.path.append(os.getcwd())

        module = import_module(args.module)
    except ImportError as exc:
        print(exc, file=sys.stderr)
        return

    writer = MarkdownWriter(sys.stdout)
    write_module(writer, module)


if __name__ == '__main__':
    main()
