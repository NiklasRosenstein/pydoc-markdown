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

""" Provides the #CrossrefProcessor that replaces cross references in
docstrings with actual hyperlinks. """

from nr.databind.core import Struct
from nr.interface import implements, override
from pydoc_markdown.interfaces import Processor
import logging
import re

logger = logging.getLogger(__name__)


@implements(Processor)
class CrossrefProcessor(Struct):

  @override
  def process(self, graph, resolver):
    graph.visit(lambda x: self._preprocess_refs(x, resolver))

  def _preprocess_refs(self, node, resolver):
    if not resolver or not node.docstring:
      return

    def handler(match):
      ref = match.group('ref')
      parens = match.group('parens') or ''
      trailing = (match.group('trailing') or '').lstrip('#')
      # Remove the dot from the ref if its trailing (it is probably just
      # the end of the sentence).
      has_trailing_dot = False
      if trailing and trailing.endswith('.'):
        trailing = trailing[:-1]
        has_trailing_dot = True
      elif not parens and ref.endswith('.'):
        ref = ref[:-1]
        has_trailing_dot = True
      href = resolver.resolve_ref(node, ref)
      if href:
        result = '[`{}`]({})'.format(ref + parens + trailing, href)
      else:
        logger.warning('ref "%s" could not be resolved in %s "%s" (%s)',
          ref, type(node).__name__, node.path(), node.location)
        result = '`{}`'.format(ref + parens)
      # Add back the dot.
      if has_trailing_dot:
        result += '.'
      return result

    node.docstring = re.sub(
      r'\B#(?P<ref>[\w\d\._]+)(?P<parens>\(\))?(?P<trailing>#[\w\d\._]+)?',
      handler,
      node.docstring)
