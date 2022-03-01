# Pydoc-Markdown

![Python versions](https://img.shields.io/pypi/pyversions/pydoc-markdown?style=for-the-badge)
[![Pypi version](https://img.shields.io/pypi/v/pydoc-markdown?style=for-the-badge)](https://pypi.org/project/pydoc-markdown/)
[![Build status](https://img.shields.io/github/workflow/status/NiklasRosenstein/pydoc-markdown/Python%20package?style=for-the-badge)](https://github.com/NiklasRosenstein/pydoc-markdown/actions)

Pydoc-Markdown is a tool to create Python API documentation in Markdown format. Instead of executing your Python
code like so many other documentation tools, it parses it using [docspec][] instead. To run Pydoc-Markdown, you
need to use at least Python 3.7.

[>> Go to the Documentation][Documentation]

  [contrib]: https://github.com/NiklasRosenstein/pydoc-markdown/blob/develop/.github/CONTRIBUTING.md
  [docspec]: https://niklasrosenstein.github.io/docspec/
  [Documentation]: https://niklasrosenstein.github.io/pydoc-markdown/
  [MkDocs]: https://www.mkdocs.org/
  [Novella]: https://niklasrosenstein.github.io/novella/
  [Novella build backend]: https://niklasrosenstein.github.io/pydoc-markdown/usage/novella/

### Installation

I recommend to install Pydoc-Markdown using Pipx.

    $ pipx install pydoc-markdown[novella]

### Features

* Understands multiple documentation styles (Sphinx, Google, Pydoc-Markdown specific) and converts them to properly
  formatted Markdown
* Can parse docstrings for variables thanks to [docspec][] (`#:` block before or string literal after the statement)
* Generates links to other API objects per the documentation syntax (e.g. `#OtherClass` for the Pydoc-Markdown style)

### News

Starting with __4.6.0__, development focuses on integrating with [Novella][] and use it as a replacement for
tool-specific renderers thus far provided directly by Pydoc-Markdown (i.e. integrations with MkDocs, Hugo and
Docusuraus). Such integrations are/will be provided by Novella instead.

With the Novella integration, you can now place generated API content in Markdown format inline with your
existing Markdown documentation source files using `@pydoc` tags. Check out the [Documentation][] for more
information on how to use Pydoc-Markdown with Novella.

The old style of using Pydoc-Markdown with a YAML or PyProject configuration to generate files and kick off the
build is now deprecated but will be maintained for the foreseeable future (at least until the next major version
bump). It is strongly recommended to migrate your existing projects to using the Novella build backend.

### Contributing to Pydoc-Markdown

All contributions are welcome! Check out the [Contribution Guidelines][contrib].

### Questions / Need help?

Feel free to open a topic on [GitHub Discussions](https://github.com/NiklasRosenstein/pydoc-markdown/discussions)!
