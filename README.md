  [MkDocs]: https://www.mkdocs.org/

<img src="https://github.com/NiklasRosenstein/pydoc-markdown/workflows/Python%20package/badge.svg"> <img src="https://readthedocs.org/projects/pydoc-markdown/badge/?version=latest&style=flat">

# Pydoc-Markdown

Pydoc-Markdown is a tool and library to create Python API documentation in
Markdown format based on `lib2to3`, allowing it to parse your Python code
without executing it.

Pydoc-Markdown requires Python 3.6 or newer, however the code that you want to
generate API documentation for can be for any Python version.

[>> Go to the Documentation](https://pydoc-markdown.readthedocs.io/en/latest/)

## Features

* Understands multiple doc styles (Sphinx, Google, Pydoc-Markdown)
* Supports assignment docstrings (`#:` block before or string literal after the statement)
* Links references to other documented API objects [WIP]
* [MkDocs][], [Hugo](https://gohugo.io/) and [Docusaurus](https://v2.docusaurus.io/) integration

## Installation

Install Pydoc-Markdown from PyPI:

    $ pipx install 'pydoc-markdown>=3.0.0,<4.0.0'

## Quickstart (MkDocs)

    $ pipx install mkdocs
    $ pydoc-markdown --bootstrap mkdocs
    $ pydoc-markdown --bootstrap readthedocs
    $ pydoc-markdown --server --open

What this does:

1. Install [MkDocs][]
2. Create a `pydoc-markdown.yml` file in the current directory
3. Create files to render your documentation on [readthedocs.org](https://readthedocs.org/)
3. Render Markdown files from the Python modules/packages in your current
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
