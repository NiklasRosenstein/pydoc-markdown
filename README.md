# pydoc-markdown

Pydoc-markdown produces Markdown API documentation from Python code.

    $ pydoc-markdown --modules mymodule

### Project state

* Basic parsing with `lib2to3` is implemented
* Basic CLI implemented
* Planned features
    * Proper parsing of Markdown additions (eg. references)
    * MkDocs renderer
    * Take hints in Python docs (eg. `# doc: ignore`)
    * Capture `TODO` and `NOTE` comments in classes and functions

> Note that Pydoc-Markdown inherits the quirks of lib2to3. For example, while
> `def test(print=builtins.print):` is valid Python 3 code, lib2to3 does not
> accept it (state Python 3.7).

## Get started

Create a `pydoc-markdown.yml` configuration file:

```yml
loaders:
  - type: python
    modules: [my_python_module]
```

Install Pydoc-markdown from GitHub:

```
$ pip install git+https://github.com/NiklasRosenstein/pydoc-markdown.git@develop
```

Then run:

```
$ pydoc-markdown > my_python_module.md
```

Alternatively, you can do the same in a single command:

```
$ pydoc-markdown --loader python --python-modules
```

## Syntax

Just use Markdown syntax in your docstrings. There are some special treatments
applied by the `pydocmd` processor though.

* `[[my_function()]]` is a reference to a function (resolved in the current
  static scope of the docstring)
* `# Parameters` in a docstring will be converted to just bold text
