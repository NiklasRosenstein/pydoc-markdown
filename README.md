  [MkDocs]: https://www.mkdocs.org/

![Python versions](https://img.shields.io/pypi/pyversions/pydoc-markdown?style=for-the-badge)
[![Pypi version](https://img.shields.io/pypi/v/pydoc-markdown?style=for-the-badge)](https://pypi.org/project/pydoc-markdown/)
[![Build status](https://img.shields.io/github/workflow/status/NiklasRosenstein/pydoc-markdown/Python%20package?style=for-the-badge)](https://github.com/NiklasRosenstein/pydoc-markdown/actions)
[![Docs status](https://img.shields.io/readthedocs/pydoc-markdown?style=for-the-badge)](https://pydoc-markdown.readthedocs.io/en/latest/)

# Pydoc-Markdown

Pydoc-Markdown is a tool and library to create Python API documentation in
Markdown format based on `lib2to3`, allowing it to parse your Python code
without executing it.

Pydoc-Markdown requires Python 3.7 or newer, however the code that you want to
generate API documentation for can be for any Python version.

[>> Go to the Documentation](https://pydoc-markdown.readthedocs.io/en/latest/)

## Features

* Understands multiple doc styles (Sphinx, Google, Pydoc-Markdown)
* Supports assignment docstrings (`#:` block before or string literal after the statement)
* Links references to other documented API objects [WIP]
* [MkDocs][], [Hugo](https://gohugo.io/) and [Docusaurus](https://v2.docusaurus.io/) integration

## Installation

Install Pydoc-Markdown from PyPI:

    $ pipx install 'pydoc-markdown>=4.0.0,<5.0.0'

## Quickstart (MkDocs)

    $ pipx install mkdocs
    $ pydoc-markdown --bootstrap mkdocs
    $ pydoc-markdown --bootstrap readthedocs
    $ pydoc-markdown --server --open

What this does:

1. Install [MkDocs][]
2. Create a `pydoc-markdown.yml` file in the current directory
3. Create files to render your documentation on [readthedocs.org](https://readthedocs.org/)
4. Render Markdown files from the Python modules/packages in your current
   working directory and run MkDocs to open a live-preview of the page.

## Quickstart (Hugo)

    $ pydoc-markdown --bootstrap hugo
    $ pydoc-markdown --server --open
  
What this does:

1. Create a `pydoc-markdown.yml` file in the current directory
2. Render Markdown files from the Python modules/packages in your current working directory
   and run Hugo to open a live-preview of the page. If Hugo is not available on your system,
   it will be downloaded automatically.

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
