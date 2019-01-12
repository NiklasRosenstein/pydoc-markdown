## Pydoc-Markdown

_Pydoc-Markdown_ generates API documentation from Python code in Markdown
format as a single file or a directory structure suitable for MkDocs. It
uses `lib2to3` to parse the the Python code for declarations, their comments
and docstrings.

> Note that Pydoc-Markdown inherits the quirks of lib2to3. For example, while
> `def test(print=builtins.print):` is valid Python 3 code, lib2to3 does not
> accept it (state Python 3.7).

### Usage

To generate a single Markdown file for a Python module or package, specify
the path to it on the command-line. This will output the full API
documentation as Markdown.

    pydoc-markdown mymodule.py

Use the MkDocs renderer to produce a suitable directory structure:

    pydoc-markdown mymodule.py --renderer=mkdocs --mkdocs-source-directory=./out
    cd out
    mkdocs serve

### Current State

* Alpha development phase
* Basic parsing with `lib2to3` is implemented
* Very basic CLI that can render Markdown from a Python source file

### Upcoming Features

* Usable command-line interface
* Ability to parse whole packages and not just single files
* Parse docstrings to produce proper markdown (and also support basic Sphinx syntax)
* Configurable Markdown renderer that outputs in a format suitable for MkDocs

### Far-future

* Actually linking between sections (which use the cross-reference syntax)
* Take hints for documentation in Python comments (eg. ignore a member)
* Capture TODO and NOTE comments in classes and function and (optionally)
  include them in the documentation
