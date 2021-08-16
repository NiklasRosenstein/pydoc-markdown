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
Loads Python source code.
"""

import dataclasses
import logging
import os
import sys
import typing as t

import docspec
import docspec_python

from pydoc_markdown.interfaces import Context, Loader

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class PythonLoader(Loader):
  """
  This implementation of the #Loader interface parses Python modules and packages using
  #docspec_python. See the options below to control which modules and packages are being
  loaded and how to configure the parser.

  With no #modules or #packages set, the #PythonLoader will discover available modules
  in the current and `src/` directory.

  __lib2to3 Quirks__

  Pydoc-Markdown doesn't execute your Python code but instead relies on the
  `lib2to3` parser. This means it also inherits any quirks of `lib2to3`.

  _List of known quirks_

  * A function argument in Python 3 cannot be called `print` even though
    it is legal syntax
  """

  #: A list of module names that this loader will search for and then parse.
  #: The modules are searched using the #sys.path of the current Python
  # interpreter, unless the #search_path option is specified.
  modules: t.Optional[t.List[str]] = None

  #: A list of package names that this loader will search for and then parse,
  #: including all sub-packages and modules.
  packages: t.Optional[t.List[str]] = None

  #: The module search path. If not specified, the current #sys.path is
  #: used instead. If any of the elements contain a `*` (star) symbol, it
  #: will be expanded with #sys.path.
  search_path: t.Optional[t.List[str]] = None

  #: List of modules to ignore when using module discovery on the #search_path.
  ignore_when_discovered: t.Optional[t.List[str]] = dataclasses.field(default_factory=lambda: ['test', 'tests', 'setup'])

  #: Options for the Python parser.
  parser: docspec_python.ParserOptions = dataclasses.field(default_factory=docspec_python.ParserOptions)

  #: The encoding to use when reading the Python source files.
  encoding: t.Optional[str] = None

  def __post_init__(self) -> None:
    self._context: t.Optional[Context] = None

  def get_effective_search_path(self) -> t.List[str]:
    if self.search_path is None:
      search_path = ['.', 'src'] if self.modules is None else list(sys.path)
    else:
      search_path = list(self.search_path)
      if '*' in search_path:
        index = search_path.index('*')
        search_path[index:index+1] = sys.path
    return [os.path.join(self._context.directory, x) for x in search_path]

  # Loader

  def load(self) -> t.Iterable[docspec.Module]:
    search_path = self.get_effective_search_path()
    modules = list(self.modules or [])
    packages = list(self.packages or [])
    do_discover = (self.modules is None and self.packages is None)

    if do_discover:
      for path in search_path:
        try:
          discovered_items = list(docspec_python.discover(path))
        except FileNotFoundError:
          continue

        logger.info(
          'Discovered Python modules %s and packages %s in %r.',
          [x.name for x in discovered_items if isinstance(x, docspec_python.DiscoveryResult.Module)],
          [x.name for x in discovered_items if isinstance(x, docspec_python.DiscoveryResult.Package)],
          path,
        )

        for item in discovered_items:
          if item.name in self.ignore_when_discovered:
            continue
          if isinstance(item, docspec_python.DiscoveryResult.Module):
            modules.append(item.name)
          elif isinstance(item, docspec_python.DiscoveryResult.Package):
            packages.append(item.name)

    logger.info(
      'Load Python modules (search_path: %r, modules: %r, packages: %r, discover: %s)',
      search_path, modules, packages, do_discover
    )

    return docspec_python.load_python_modules(
      modules=modules,
      packages=packages,
      search_path=search_path,
      options=self.parser,
      encoding=self.encoding,
    )

  # PluginBase

  def init(self, context: Context) -> None:
    self._context = context
