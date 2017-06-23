## pydocmd

&ndash; *insipired by the [Keras] Documentation*

Pydocmd uses [MkDocs] and extended [Markdown] syntax to generate beautiful
Python API documentation.

  [MkDocs]: http://www.mkdocs.org/
  [Markdown]: https://pythonhosted.org/Markdown/
  [Extension API]: https://niklasrosenstein.github.io/pydoc-markdown/extensions/loader/
  [Keras]: https://keras.io/

__Todo__

- [x] Support `+` suffix to include documented members of a module/class
- [ ] Expand and link cross-references (eg. `#SomeClass`)
- [ ] Parse, format and link types listed in parameter/member/raise/return type
      docstrings (eg. `someattr (int): This is...`)

## Installation

    pip install pydoc-markdown
    pip install git+https://github.com/NiklasRosenstein/pydoc-markdown.git  # latest development version

## Usage

Pydocmd can generate plain Markdown files from Python modules using the
`pydocmd simple` command. Specify one or more module names on the command-line.
Supports the `+` syntax to include members of the module (or `++` to include
members of the members, etc.)

    pydocmd simple mypackage+ mypackage.mymodule+ > docs.md

Alternatively, pydocmd wraps the MkDocs command-line interface and generates
the markdown pages beforehand. Simply use `pydocmd build` to build the
documentation, or `pydocmd serve` to serve the documentation on a local HTTP
server. The `pydocmd gh-deploy` from MkDocs is also supported.

A configuration file `pydocmd.yml` is required to use pydocmd in this mode.
Below is an example configuration. To get started, create `docs/` directory
and a file `pydocmd.yml` inside of it. Copy the configuration below and
adjust it to your needs, then run `pydocmd build` from the `docs/` directory.

```yaml
site_name: "My Documentation"

# This tells pydocmd which pages to generate from which Python modules,
# functions and classes. At the first level is the page name, below that
# is a tree of Python member names (modules, classes, etc.) that should be
# documented. Higher indentation leads to smaller header size.
generate:
- baz/cool-stuff.md:
  - foobar.baz:
    - foobar.baz.CoolClass+     # (+ to include members)
    - foobar.baz.some_function
- baz/more-stuff.md:
  - foobar.more++               # (++ to include members, and their members)

# MkDocs pages configuration. The `<<` operator is sugar added by pydocmd
# that allows you to use an external Markdown file (eg. your project's README)
# in the documentation. The path must be relative to current working directory.
pages:
- Home: index.md << ../README.md
- foobar.baz:
  - Cool Stuff: baz/cool-stuff.md

# These options all show off their default values. You don't have to add
# them to your configuration if you're fine with the default.
docs_dir: sources
gens_dir: _build/pydocmd     # This will end up as the MkDocs 'docs_dir'
site_dir: _build/site
theme:    readthedocs
loader:   pydocmd.loader.PythonLoader
preprocessor: pydocmd.preprocessor.Preprocessor

# Additional search path for your Python module. If you use Pydocmd from a
# subdirectory of your project (eg. docs/), you may want to add the parent
# directory here.
additional_search_paths:
- ..
```

## Syntax

### Cross-references

Symbols in the same namespace may be referenced by using a hash-symbol (`#`)
directly followed by the symbols' name, including relative references. Note that
using parentheses for function names is encouraged and will be ignored and
automatically added when converting docstrings. Examples: `#ClassName.member` or
`#mod.function()`.

For absolute references for modules or members in names that are not available
in the current global namespace, `#::mod.member` must be used (note the two
preceeding two double-colons).

For long reference names where only some part of the name should be displayed,
the syntax `#X~some.reference.name` can be used, where `X` is the number of
elements to keep. If `X` is omitted, it will be assumed 1. Example:
`#~some.reference.name` results in only `name` being displayed.

In order to append additional characters that are not included in the actual
reference name, another hash-symbol can be used, like `#Signal#s`.

**pydoc-markdown** can be extended to find other cross-references using the
[Extension API].

### Sections

Sections can be generated with the Markdown `# <Title>` syntax. It is important
to add a whitespace after the hash-symbol (`#`), as otherwise it would represent
a cross-reference. Some special sections alter the rendered result of their
content, including

- Arguments (1)
- Parameters (1)
- Attributes (1)
- Members (1)
- Raises (2)
- Returns (2)

(1): Lines beginning with `<ident> [(<type>[, ...])]:` are treated as
argument/parameter or attribute/member declarations. Types listed inside the
parenthesis (optional) are cross-linked, if possible. For attribute/member
declarations, the identifier is typed in a monospace font.

(2): Lines beginning with `<type>[, ...]:` are treated as raise/return type
declarations and the type names are cross-linked, if possible.

Lines following a name's description are considered part of the most recent
documentation unless separated by another declaration or an empty line. `<type>`
placeholders can also be tuples in the form `(<type>[, ...])`.

### Code Blocks

GitHub-style Markdown code-blocks with language annotations can be used.

    ```python
    >>> for i in range(100):
    ...
    ```

---

## Changes

### v2.0.2 (tip)

- Fix #25 -- Text is incorrectly rendered as code

### v2.0.1

- Support `additional_search_path` key in configuration
- Render headers as HTML `<hX>` tags rather than Markdown tags, so we
  assign a proper ID to them
- Fix #21 -- AttributeError: 'module' object has no attribute 'signature'
- Now requires the `six` module
- FIx #22 -- No blank space after header does not render codeblocks

### v2.0.0

- Complete overhaul of **pydoc-markdown** employing MkDocs and the Markdown module.

---

<p align="center">Copyright &copy; 2017  Niklas Rosenstein</p>
