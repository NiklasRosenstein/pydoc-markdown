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
* Cross-page (and cross-project) links in API documentation

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
is defined as follows:

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

It is automatically applied when using the Pydoc-Markdown CLI to render
Markdown documentation for Python modules on the fly (without a YAML
configuration file). Example:

    $ cat <<EOF >a.py
    def say_hello(name: str):
      """ Says hello to the person specified with *name*.

      :param name: The person to say hello to.
      :raises ValueError: If *name* is empty.
      :returns: Nothing """
      # ...
    EOF
    $ pydoc-markdown -m a -I .

<details><summary>Expand to see the generated Markdown</summary>

---

<a name=".a"></a>
## a

<a name=".a.say_hello"></a>
#### say\_hello

```python
say_hello(name: str)
```

Says hello to the person specified with *name*.

**Arguments**:

- `name`: The person to say hello to.

**Raises**:

- `ValueError`: If *name* is empty.

**Returns**:

Nothing

---

</details>

To jumpstart your documentation endavours, try running `pydoc-markdown --bootstrap` or
`pydoc-markdown --bootsrap-mkdocs` to generate a template configuration file.

If a configuration file exists, then the CLI needs to be invoked without
arguments, or with one argument that specifies the path to the configuration
file. When using the `mkdocs` renderer, you may add the `--watch-and-serve`
and `--open` arguments for smooth live-feedback.

    $ pydoc-markdown ./pydoc-markdown.yaml -wo

## lib2to3 Quirks

Pydoc-Markdown doesn't execute your Python code but instead relies on the
`lib2to3` parser. This means it also inherits any quirks of `lib2to3`.

__List of known quirks__

* A function argument in Python 3 cannot be called `print` even though
  it is legal syntax
