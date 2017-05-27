**pydoc-markdown** uses [MkDocs] and extended [Markdown] syntax to generate
beautiful Python API documentation. It is highly configurable and can be
extended to work with arbitrary programming languages, see the [Extension API].
Highly insipired by the [Keras] Documentation.

  [MkDocs]: www.mkdocs.org/
  [Markdown]: https://pythonhosted.org/Markdown/
  [Extension API]: https://niklasrosenstein.github.io/pydoc-markdown/extensions/loader/
  [Keras]: https://keras.io/

__Todo__

- [x] Support `+` suffix to include documented members of a module/class
- [ ] Expand and link cross-references (eg. `#SomeClass`)
- [ ] Parse, format and link types listed in parameter/member/raise/return type
      docstrings (eg. `someattr (int): This is...`)

__Synopsis__

    pydocmd simple <module>[.<member>][+] [...]
        Output Python markdown documentation to stdout for the specified
        module or module member. Add one or more `+` characters for every
        additional level to include in the documentation. Multiple such
        arguments can be specified.
    pydocmd generate
        Build Markdown files from the `generate` configuration in the
        `pydocmd.yml` file.
    pydocmd new
        Start a new PydocMd project. Generates a default `pydocmd.yml`
        file in the current directory.
    pydocmd {build,serve,gh-deploy,json}
        Wrapper around the MkDocs command-line. Runs `pydocmd generate`
        before invoking MkDocs with the specified subcommand.

## Building

The `pydocmd` command is a wrapper around `mkdocs` and supports the same
commands. It will simply autogenerate the documentation files and then invoke
MkDocs. If you only want to run the auto-generation, simply use the `generate`
subcommand.

    $ pydocmd --help
    usage: pydocmd [-h] {generate,build,gh-deploy,json,new,serve, simple} [subargs...]

    positional arguments:
    {generate,build,gh-deploy,json,new,serve, simple}

    optional arguments:
    -h, --help            show this help message and exit

## Configuration

**pydoc-markdown** only takes over the task of generating the Markdown
documentation that can then be processed with [MkDocs]. However, it can still
combine both parts of the build process in a single command. You can put all
configuration for [MkDocs] into the `pydocmd.yml` configuration, or have
it in a separate `mkdocs.yml` file.

__pydocmd.yml__

```yaml
site_name: "foobar Documentation"

generate:
- baz/cool-stuff.md:
  - foobar.baz:                 # Module docstring
    # Indenting the following items to give them a smaller header size
    - foobar.baz.CoolClass+     # Class docstring (+ to include members)
    - foobar.baz.some_function  # Function docstring
- baz/more-stuff.md:
  - foobar.more++               # foobar.more module, plus 2 more levels (eg.
                                # classes and their members)

# MkDocs pages configuration, with some sugar.
pages:
- Home: index.md << ../README.md
- foobar.baz:
  - Cool Stuff: baz/cool-stuff.md

docs_dir: sources                                 # default
gens_dir: _build/pydocmd                          # default (-> MkDocs docs_dir)
site_dir: _build/site                             # default
theme:    readthedocs                             # default
loader:   pydocmd.loader.PythonLoader             # default
preprocessor: pydocmd.preprocessor.Preprocessor   # default
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

### v2.0.1

- Support `additional_search_path` key in configuration
- Render headers as HTML `<hX>` tags rather than Markdown tags, so we
  assign a proper ID to them
- Fix #21 -- AttributeError: 'module' object has no attribute 'signature'

### v2.0.0

- Complete overhaul of **pydoc-markdown** employing MkDocs and the Markdown module.

---

<p align="center">Copyright &copy; 2017  Niklas Rosenstein</p>
