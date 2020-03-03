# Pydoc-Markdown
<a href="https://circleci.com/gh/NiklasRosenstein/workflows/pydoc-markdown/tree/develop"><img align="right" src="https://circleci.com/gh/NiklasRosenstein/pydoc-markdown/tree/develop.svg?style=svg" alt="CircleCI"><img align="right" src="https://img.shields.io/badge/version-3.x-purple" alt="Version 3.x"></a>

Pydoc-Markdown is a tool to create Python API documentation in markdown format
based on `lib2to3`.

__Features__

* Parses the AST instead of running your code
* Understands multiple documentation styles (Sphinx, Google, Pydoc-Markdown)
* Resolves cross-references of the form `#PetType.CAT`
* Supports attribute docstrings (`#: ...` before or string literals after
  the statement)

__On the roadmap__

* Mkdocs integration (for feature parity with Pydoc-Markdown 2.x)
* Support for images (#94)
* Understand fixmes and hints in the source code (eg. `# doc: ignore`)

## Usage

  [Pipx]: https://pypi.org/project/pipx/

Pydoc-Markdown 3 is not currently available on PyPI. To install the current
development version, you can simply pass the Git repository URL to Pip. It is
recommended to install Pydoc-Markdown in isolation with [Pipx].

    $ pipx install git+https://github.com/NiklasRosenstein/pydoc-markdown.git@develop

This makes the `pydoc-markdown` command available in your command-line.

On the CLI you specify either the name of a configuration file or provide a
YAML formatted configuration. If you do not specify any arguments, the default
configuration file is loaded (`pydoc-markdown.ya?ml`).

    $ pydoc-markdown [<config>]

The configuration is composed of three main components: A list of loaders,
a list of documentation processors and a renderer. The default configuration
is defined as

```yaml
loaders:
  - type: python
processors:
  - type: filter
  - type: smart
  - type: crossref
renderer:
  - type: markdown
```

This default configuration is used automatically if no configuration is
supplied, or if you specify a YAML configuration that does not actually
override values, eg:

    $ pydoc-markdown "{}"

## lib2to3 Quirks

Pydoc-Markdown doesn't execute your Python code but instead relies on the
`lib2to3` parser. This means it also inherits any quirks of `lib2to3`.

__List of known quirks__

* A function argument in Python 3 cannot be called `print` even though
  it is legal syntax
