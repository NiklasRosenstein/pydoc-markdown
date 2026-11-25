@anchor yaml-config
# Configuration

A configuration file describes the whole pipeline: which code to **load**, how to **process** it, and how to
**render** it. Running `pydoc-markdown` with no arguments looks for, in this order:

1. `pydoc-markdown.yml`
2. `pydoc-markdown.yaml`
3. a `[tool.pydoc-markdown]` table in `pyproject.toml`

You can also pass a file name, or an inline YAML object, as the first argument:

```sh
pydoc-markdown docs/pydoc-markdown.yaml
pydoc-markdown -m my_module '{renderer: {type: markdown, render_toc: true}}'
```

To start from a template, run `pydoc-markdown --bootstrap <template>` with `base`, `mkdocs`, `hugo` or `docusaurus`.
It writes `pydoc-markdown.yaml` and refuses to overwrite an existing configuration. The `readthedocs` template is
different: it writes a `.readthedocs.yaml` for building an MkDocs site on Read the Docs (see the
[Read the Docs recipe](../recipes/readthedocs.md)).

!!! note "Quick options bypass the configuration file"

    `-m`, `-p` and `-I` build a configuration from the command line, so the configuration file is ignored
    (with a warning). To use both, name the file explicitly: `pydoc-markdown pydoc-markdown.yaml -I src` loads the file
    and applies `-I src` on top.

## Structure

The configuration has four top-level keys. All of them are optional.

| Key | What it is | Default |
| --- | --- | --- |
| `loaders` | List of plugins that load API objects. | one `python` loader |
| `processors` | List of plugins that transform API objects, in order. | `filter`, `smart`, `crossref` |
| `renderer` | The plugin that writes output. | `markdown` (to stdout) |
| `hooks` | Shell commands to run before and after rendering. | none |

Every plugin is selected with `type`; all other keys are that plugin's options, listed in the
[reference](../reference/loaders.md).

=== "pydoc-markdown.yaml"

    ```yaml
    loaders:
      - type: python
        search_path: [src]
    processors:
      - type: filter
      - type: smart
      - type: crossref
    renderer:
      type: mkdocs
      pages:
        - title: API Documentation
          name: index
          contents: [school.*]
          exclude: [school.admin]
    ```

=== "pyproject.toml"

    ```toml
    [[tool.pydoc-markdown.loaders]]
    type = "python"
    search_path = ["src"]

    [[tool.pydoc-markdown.processors]]
    type = "filter"

    [[tool.pydoc-markdown.processors]]
    type = "smart"

    [[tool.pydoc-markdown.processors]]
    type = "crossref"

    [tool.pydoc-markdown.renderer]
    type = "mkdocs"

    [[tool.pydoc-markdown.renderer.pages]]
    title = "API Documentation"
    name = "index"
    contents = ["school.*"]
    exclude = ["school.admin"]
    ```

Relative **input** paths are resolved from the directory that contains the configuration file: the loader's
`search_path`, a page's `source`, a source linker's `root`, and the working directory of hooks. Relative **output**
paths are resolved from the directory you run `pydoc-markdown` in: the Markdown renderer's `filename`, the MkDocs
renderer's `output_directory`, the Hugo renderer's `build_directory` and the Docusaurus renderer's `docs_base_path`.
Run Pydoc-Markdown from your project root, or use absolute paths, if the configuration lives in a subdirectory.

## Loaders

The [`python` loader](../reference/loaders.md) is the only built-in loader. Without `modules` or `packages`, it
discovers every module and package in its `search_path` (skipping `test`, `tests` and `setup` by default).
If `search_path` is not set, it defaults to `.` and `src` next to the configuration file, or to Python's `sys.path` when
only `modules` are given. Put `"*"` into `search_path` to add `sys.path` to your own entries.

```yaml
loaders:
  - type: python
    search_path: [src]
    packages: [my_package]    # a package and all its submodules
    modules: [my_script]      # a single module
```

## Processors

Processors run in the listed order. Setting `processors` replaces the default list entirely, so include every processor
you want. [Docstrings and processors](docstrings.md) explains how to choose them.

## Renderer

The default `markdown` renderer prints a single Markdown document to stdout, or writes it to `filename`. Other
renderers produce a site tree; see [Static site generators](static-site-generators.md).

## Pages

The `mkdocs` and `hugo` renderers take a `pages` list. Each page has a `title` and may have:

| Option | Meaning |
| --- | --- |
| `name` | File name without extension. Defaults to a slug of `title`; use `index` for the landing page. |
| `contents` | Glob patterns of API objects to render on this page, e.g. `[my_pkg, my_pkg.*]`. |
| `exclude` | Glob patterns of API objects to leave out. Applied after `contents` and takes precedence over it, so excluding a module or class also removes all of its members, even ones that `contents` matches. Parents of objects that remain on the page are kept. |
| `source` | A file to copy as the page content, e.g. `README.md`. Relative to the configuration file. |
| `href` | Don't generate a file; link to this URL in the navigation instead. |
| `children` | Nested pages. |

Patterns match the fully qualified name of an API object. Note that `my_pkg.*` matches the members of `my_pkg`, but not
`my_pkg` itself. With `--server`, files referenced by `source` are watched too.

To exclude something from every page, use the [`filter` processor](docstrings.md#choosing-what-gets-documented)
instead.

## Hooks

Run shell commands before or after the render step:

```yaml
hooks:
  pre-render:
    - generate-changelog > docs/CHANGELOG.md
  post-render:
    - echo done
```

## Templating

> *New in 3.3.0. See also `pydoc_markdown.util.ytemplate`.*

YAML configuration files are pre-processed with a small [YTT](https://carvel.dev/ytt/)-like template language before
they are parsed. Lines starting with `#@` contain Python code:

* `#@ def name(): … #@ end` defines a function (YAML inside the function body is not supported).
* `key: #@ expression` substitutes the value of a Python expression. Environment variables are available as `env`.

```yaml
#@ def base_url():
#@   return "https://example.com/" + env.VERSION + "/" if env.VERSION else None
#@ end

renderer:
  type: hugo
  config:
    baseURL: #@ base_url()
```

Templating applies to YAML files only, not to `pyproject.toml`.

## Debugging a configuration

`--dump` prints the API objects after processing in docspec JSON format. Pipe it into `docspec` to get a tree:

```
$ pydoc-markdown --dump | docspec -m --dump-tree
module school
module school._pupil
| class Pupil
| | variable classes
module school._person
| class Person
| | variable name
| | variable age
[ ... ]
```

Add `--without-processors` to see what the loader found before filtering.
