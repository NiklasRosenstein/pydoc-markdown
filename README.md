## Pydoc-Markdown

_Pydoc-Markdown_ generates API documentation for Python code in Markdown format.

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
