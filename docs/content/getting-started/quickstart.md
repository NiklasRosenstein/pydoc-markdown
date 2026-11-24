# Quickstart

This page takes you from nothing to a generated Markdown file, then to a reusable configuration. It assumes your code
lives in `src/my_package/`.

## 1. Render a package to stdout

```sh
pydoc-markdown -I src -p my_package --render-toc > api.md
```

* `-I src` adds `src/` to the search path (repeatable).
* `-p my_package` documents the package and all its submodules; use `-m my_package.module` for a single module.
* `--render-toc` adds a table of contents at the top.

By default, members without a docstring and private members (names starting with `_`) are left out. Docstrings are
converted to Markdown with the [`smart` processor](../guides/docstrings.md), which detects the docstring style for you.

## 2. Move the options into a configuration file

Command-line flags are fine for a one-off; a configuration file lets you tune every option. Create one with:

```sh
pydoc-markdown --bootstrap base
```

This writes `pydoc-markdown.yml` containing the default pipeline. Point the loader at your code:

```yaml title="pydoc-markdown.yml"
loaders:
  - type: python
    search_path: [src]
    packages: [my_package]
processors:
  - type: filter
  - type: smart
  - type: crossref
renderer:
  type: markdown
  render_toc: true
  filename: api.md
```

Now run Pydoc-Markdown without arguments. It finds `pydoc-markdown.yml`, `pydoc-markdown.yaml`, or a
`[tool.pydoc-markdown]` table in `pyproject.toml`, in that order:

```sh
pydoc-markdown
```

!!! note

    `-m`, `-p` and `-I` build a configuration from the command line and **ignore** the configuration file
    (you will see a warning). To combine both, pass the file explicitly: `pydoc-markdown pydoc-markdown.yml -I src`.

## 3. Choose where the output goes

* **One Markdown file** — the `markdown` renderer, as above. See the [Markdown renderer reference](../reference/renderers/markdown.md)
  for its many formatting options.
* **A documentation site** — bootstrap with `--bootstrap mkdocs`, `hugo` or `docusaurus` and read
  [Static site generators](../guides/static-site-generators.md).
* **API docs embedded in hand-written pages** — use the [Novella integration](../guides/novella.md).

## Inspect what was loaded

If something is missing from the output, dump the API objects Pydoc-Markdown sees after processing:

```sh
pydoc-markdown --dump | docspec -m --dump-tree
```

Add `--without-processors` to see the tree before filtering.
