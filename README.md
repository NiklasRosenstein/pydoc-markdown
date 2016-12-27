**pydoc-markdown** uses [MkDocs] and extended [Markdown] syntax to generate
beautiful Python API documentation. It is highly configurable and can be
extended to work with arbitrary programming languages, see the [Extension API].

  [MkDocs]: www.mkdocs.org/
  [Markdown]: https://pythonhosted.org/Markdown/
  [Extension API]: docs/templates/extensions.md

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
  - foobar.baz                # Module docstring
  - foobar.baz.CoolClass      # Class docstring
  - foobar.baz.some_function  # Function docstring
pages:
- Home: index.md
- foobar.baz:
  - Cool Stuff: baz/cool-stuff.md

mkdocs:
  # Additional config for mkdocs
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

### v2.0.0 (devtip)

- Complete overhaul of **pydoc-markdown** employing MkDocs and the Markdown module.

---

<p align="center">Copyright &copy; 2017  Niklas Rosenstein</p>
