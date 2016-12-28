# Copyright (c) 2017  Niklas Rosenstein
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
This module implements the structural representation of an API documentation
in separate documents and symbolic names. The final documentation is rendered
from this structured representation.
"""

from __future__ import print_function


class Section(object):
  """
  A section represents an entry in a #Document that will be rendered into a
  #Document as-is. Every section may, but not necessarily, be associated with a
  symbolic name that can be cross-linked to.
  """

  def __init__(self, symbolic_name=None, content='*Empty section*'):
    self.content = content
    self.symbolic_name = symbolic_name
    self.document = None
    self.link_targets = {}

  def add_link_target(self, url):
    """
    Add a link target to the section. Note that the section must be contained
    in a #Document before this method can be used, otherwise a #RuntimeError
    will be raised.

    # Arguments
      url (str): The URL to link to.

    # Returns
      str: The name of the link target that will be added to the bottom
        of the section.

    # Raises
      RuntimeError: If the #Section is not contained in a #Document.
    """

    if not self.document:
      raise RuntimeError('Section is not in a Document')

    name = self.document.next_link_target()
    self.link_targets[name] = url
    return name

  def render(self, fp):
    if self.symbolic_name:
      print('<a name="{}"></a>\n'.format(self.symbolic_name), file=fp)
    print(self.content, file=fp)
    for name, url in self.link_targets:
      print('[{}]: {}'.format(name, url), file=fp)


class Document(object):
  """
  Represents a single document that may contain several #Section#s. Every
  document *must* have a name associated with it. This name will be used
  to construct URLs to cross-link between different documents, thus they
  must reflect the URL structure.
  """

  def __init__(self, name):
    self.name = name
    self.sections = []
    self.allocated_link_targets = 0

  def next_link_target(self):
    """
    Get the name of the next link target that is unique in this document.
    """

    try:
      return str(self.allocated_link_target)
    finally:
      self.allocated_link_target += 1

  def add(self, symbolic_name=None):
    """
    Create a new #Section with the specified *symbolic_name* and add it to the
    document.

    # Returns
      Section: The section that was created and added to the document.
    """

    section = Section(symbolic_name)
    section.document = self
    self.sections.append(section)
    return section

  def render(self, fp):
    for section in self.sections:
      section.render(fp)
