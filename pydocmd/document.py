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
import os


class Section(object):
  """
  A section represents a part of a #Document. It contains Markdown-formatted
  content that will be rendered into a file at some point.

  # Attributes
  doc (Document): The document that the section belongs to.
  identifier (str, None): The globally unique identifier of the section. This
    identifier usually matches the name of the element that the section
    describes (eg. a class or function) and will be used for cross-referencing.
  title (str, None): The title of the section. If specified, it will be
    rendered before `section.content` and the header-size will depend on
    the `section.depth`.
  depth (int): The depth of the section, defaults to 1. Currently only affects
    the header-size that is rendered for the `section.title`.
  content (str): The Markdown-formatted content of the section.
  """

  def __init__(self, doc, identifier=None, title=None, depth=1, content=None, header_type='html'):
    self.doc = doc
    self.identifier = identifier
    self.title = title
    self.depth = depth
    self.content = content if content is not None else '*Nothing to see here.*'
    self.header_type = header_type

  def render(self, stream):
    """
    Render the section into *stream*.
    """

    if self.header_type == 'html':
      print('<h{depth} id="{id}">{title}</h{depth}>\n'
        .format(depth = self.depth, id = self.identifier, title = self.title),
        file = stream)
    elif self.header_type == 'markdown':
      print('#' * self.depth, self.title, file = stream)
    else:
      raise ValueError('Invalid header type: %s' % self.header_type)
    print(self.content, file=stream)

  @property
  def index(self):
    """
    Returns the #Index that this section is associated with, accessed via
    `section.document`.
    """

    return self.document.index


class Document(object):
  """
  Represents a single document that may contain several #Section#s. Every
  document *must* have a relative URL associated with it.

  # Attributes
  index (Index): The index that the document belongs to.
  url (str): The relative URL of the document.
  """

  def __init__(self, index, url):
    self.index = index
    self.url = url
    self.sections = []


class Index(object):
  """
  The index manages all documents and sections globally. It keeps track of
  the symbolic names allocated for the sections to be able to link to them
  from other sections.

  # Attributes
  documents (dict):
  sections (dict):
  """

  def __init__(self):
    self.documents = {}
    self.sections = {}

  def new_document(self, filename, url=None):
    """
    Create a new document.

    # Arguments
    filename (str): The filename of the document. Must end with `.md`.
    url (str): The relative URL of the document. If omitted, will be
      automatically deduced from *filename* (same without the `.md` suffix).

    # Raises
    ValueError: If *filename* does not end with `.md`.
    ValueError: If *filename* is not a relative path.
    ValueError: If a document with the specified *filename* already exists.
    """

    if not filename.endswith('.md'):
      raise ValueError('filename must end with `.md`')
    if os.path.isabs(filename):
      raise ValueError('filename must be relative')
    if filename in self.documents:
      raise ValueError('document filename {!r} already used'.format(filename))
    if not url:
      url = filename[:-3]

    doc = Document(self, url)
    self.documents[filename] = doc
    return doc

  def new_section(self, doc, *args, **kwargs):
    """
    Create a new section in the specified document. The arguments for this
    method match the parameters for the #Section constructor.

    # Raises
    ValueError: If the section identifier is already used.
    """

    section = Section(doc, *args, **kwargs)
    if section.identifier:
      if section.identifier in self.sections:
        raise ValueError('section identifier {!r} already used'
          .format(section.identifier))
      self.sections[section.identifier] = section
    doc.sections.append(section)
    return section
