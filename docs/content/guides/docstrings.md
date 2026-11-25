# Docstrings and processors

Between loading your code and rendering it, Pydoc-Markdown runs a list of **processors**. Each one modifies the loaded
API objects: removing members you don't want documented, converting docstrings to Markdown, or resolving
cross-references. When you don't configure any, this list is used:

```yaml
processors:
  - type: filter
  - type: smart
  - type: crossref
```

Order matters: filter first, so you don't spend time converting docstrings that won't be rendered; resolve
cross-references last, once docstrings are Markdown.

## Choosing what gets documented

The [`filter` processor](../reference/processors.md) removes API objects. By default it drops:

* objects without a docstring (`documented_only: true`),
* private members, i.e. names that start but don't end with `_` (`exclude_private: true`),
* special members such as `__all__` and `__path__` (`exclude_special: true`).

Modules are never removed unless they are empty and `skip_empty_modules: true` is set.

To keep undocumented members, or to write your own rule, configure the processor explicitly. `expression` is a Python
expression that receives `name`, `obj` and `default` (the result of the built-in rules):

```yaml
processors:
  - type: filter
    documented_only: false
    expression: not name.startswith("test_") and default()
  - type: smart
  - type: crossref
```

To include or exclude objects on a single page only, use the page's `contents` and `exclude` globs instead (see
[Configuration](configuration.md#pages)).

## Docstring styles

| Style | Example section | Processor |
| --- | --- | --- |
| Google | `Args:` / `Returns:` | `google`, or `sphinx` with `style: GOOGLE` |
| Sphinx / reST | `:param x:` / `:return:` | `sphinx` |
| NumPy | `Parameters` underlined with `----------` | `sphinx` with `style: NUMPYDOC` |
| Epydoc | `@param x:` | `sphinx` with `style: EPYDOC` |
| Pydoc-Markdown | `# Arguments` | `pydocmd` |

### `smart` — detect the style per docstring (default)

The `smart` processor inspects each docstring and hands it to the `sphinx`, `google` or `pydocmd` processor. This
works well for most projects, including ones that mix styles. If detection picks the wrong style for a particular
docstring, force it by adding a marker anywhere in that docstring; the marker is removed from the output:

```python
def frobnicate(x):
    """Frobnicate *x*.

    @doc:fmt:google
    """
```

Valid markers are `@doc:fmt:google`, `@doc:fmt:sphinx` and `@doc:fmt:pydocmd`.

### `sphinx` — one parser for reST, Google, NumPy and Epydoc

The `sphinx` processor uses [docstring-parser](https://pypi.org/project/docstring-parser/). By default it
auto-detects the style; set `style` to `REST`, `GOOGLE`, `NUMPYDOC` or `EPYDOC` if your whole project uses one:

```yaml
processors:
  - type: filter
  - type: sphinx
    style: NUMPYDOC
  - type: crossref
```

### `google` and `pydocmd`

`google` converts Google-style sections (`Args:`, `Returns:`, `Raises:`, `Attributes:`, …) to Markdown lists.
`pydocmd` handles Pydoc-Markdown's own Markdown-like style:

```python
def connect(host, port=80):
    """
    Open a connection.

    # Arguments
    host (str): The host name.
    port (int): The port.

    # Returns
    Connection: The open connection.
    """
```

New projects should prefer a standard style (Google, NumPy or reST); `pydocmd` mainly exists for projects that
already use it.

## Variable docstrings

Thanks to docspec, module, class and instance variables can be documented, either with a `#:` comment block before the
assignment or a string literal right after it:

```python
#: The default timeout in seconds.
TIMEOUT = 30

RETRIES = 3
"""How often a request is retried."""
```

## Cross-references

The `crossref` processor turns `#Name` references in docstrings into links, if the renderer can resolve the target
(the `markdown`, `mkdocs` and `hugo` renderers can):

```text
Returns a #Connection.            -> link to Connection
See #Connection.close().          -> link to a member
Returns many #Connection#s.       -> link to Connection with the text "Connections"
```

The link text is the reference itself, plus anything after a second `#`. References that can't be resolved are
rendered as inline code.
