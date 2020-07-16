  [MkDocs]: https://www.mkdocs.org/

# Pydoc-Markdown
<a href="https://circleci.com/gh/NiklasRosenstein/workflows/pydoc-markdown/tree/develop"><img align="right" src="https://circleci.com/gh/NiklasRosenstein/pydoc-markdown/tree/develop.svg?style=svg" alt="CircleCI"><img align="right" src="https://img.shields.io/badge/version-3.x-purple" alt="Version 3.x"></a>

Pydoc-Markdown is a tool and library to create Python API documentation in
Markdown format based on `lib2to3`, allowing it to parse your Python code
without executing it.

Pydoc-Markdown requires Python 3.6 or newer.

[>> Go to the Documentation](https://pydoc-markdown.readthedocs.io/en/latest/)

__Features__

* Understands multiple doc styles (Sphinx, Google, Pydoc-Markdown)
* Supports assignment docstrings (`#:` block before or string literal after the statement)
* Links references to other documented API objects [WIP]
* [MkDocs][] and [Hugo](https://gohugo.io/) integration

__Installation__

Install Pydoc-Markdown from PyPI:

    $ pipx install 'pydoc-markdown>=3.0.0,<4.0.0'

__Quickstart__

    $ pipx install mkdocs
    $ pydoc-markdown --bootstrap mkdocs
    $ pydoc-markdown --bootstrap readthedocs
    $ pydoc-markdown --server --open-browser

What this does:

1. Install [MkDocs][]
2. Create  `pydoc-markdown.yaml` file in the current directory
3. Render Markdown files from the Python modules/packages in your current
   working directory and open a browser to the live-reloading HTML page
   generated by MkDocs.

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
