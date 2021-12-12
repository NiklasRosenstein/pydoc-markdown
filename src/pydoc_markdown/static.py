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


#: The default configuration that is rendered when using --bootstrap base.
DEFAULT_CONFIG = '''
loaders:
  - type: python
processors:
  - type: filter
  - type: smart
  - type: crossref
renderer:
  type: markdown
'''.lstrip()


#: The default configuration that is rendered when uing --bootstrap mkdocs.
DEFAULT_MKDOCS_CONFIG = '''
loaders:
  - type: python
processors:
  - type: filter
  - type: smart
  - type: crossref
renderer:
  type: mkdocs
  pages:
    - title: Home
      name: index
      source: README.md
    - title: API Documentation
      children:
        - title: my_project
          contents: [ my_project, my_project.* ]
  mkdocs_config:
    site_name: My Project
    theme: readthedocs
    repo_url: https://github.com/Me/my-project
'''.lstrip()


#: The default configuration that is rendered when using --bootstrap hugo.
DEFAULT_HUGO_CONFIG = '''
loaders:
  - type: python
processors:
  - type: filter
  - type: smart
  - type: crossref
renderer:
  type: hugo
  config:
    title: My Project
    theme: {clone_url: "https://github.com/alex-shpak/hugo-book.git"}
  # The "book" theme only renders pages in "content/docs" into the nav.
  content_directory: content/docs
  default_preamble: {menu: main}
  pages:
    - title: Home
      name: index
      source: README.md
    - title: API Documentation
      children:
        - title: my_project
          contents: [ my_project, my_project.* ]
'''.lstrip()

DEFAULT_DOCUSAURUS_CONFIG = '''
loaders:
  - type: python
processors:
  - type: filter
    skip_empty_modules: true
  - type: smart
  - type: crossref
renderer:
  type: docusaurus
  docs_base_path: docs
  relative_output_path: reference
  relative_sidebar_path: sidebar.json
  sidebar_top_level_label: 'Reference'
'''.lstrip()


#: Default configuration for Read the Docs to use Pydoc-Markdown.
READTHEDOCS_FILES = {
  '.readthedocs.yml': '''
version: 2
mkdocs: {}  # tell readthedocs to use mkdocs
python:
  version: 3.7
  install:
  - method: pip
    path: .
  - requirements: docs/requirements.txt
'''.lstrip(),

  'docs/.readthedocs-custom-steps.yml': '''
steps:
- |
  pydoc-markdown --build --site-dir "$PWD/_build/html"
'''.lstrip(),

  'docs/requirements.txt': '''
readthedocs-custom-steps==0.5.1
'''.lstrip(),
}
