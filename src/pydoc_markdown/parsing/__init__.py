
"""
The #pydoc_markdown.parsing module parses Python source files with #lib2to3
to generate a complete reflection of a modules' structure.
"""

import lib2to3.refactor
import textwrap

from .reflection import *
from .parser import Parser, parse_file
