# Static site generators

Pydoc-Markdown has renderers that write a complete source tree for three static site generators. Each one wraps the
[Markdown renderer](../reference/renderers/markdown.md) (configured under its `markdown` key) and adds the files and
layout the generator expects.

| Renderer | Output | `--server` | `--build` | Bootstrap |
| --- | --- | :---: | :---: | --- |
| [`mkdocs`](../reference/renderers/mkdocs.md) | `mkdocs.yml` and pages in `build/docs/` | ✓ | ✓ | `--bootstrap mkdocs` |
| [`hugo`](../reference/renderers/hugo.md) | Hugo `config.toml` and pages in `build/docs/` | ✓ | ✓ | `--bootstrap hugo` |
| [`docusaurus`](../reference/renderers/docusaurus.md) | Pages and `sidebar.json` inside your Docusaurus project | — | — | `--bootstrap docusaurus` |

!!! tip "Hand-written pages"

    Pages don't have to be generated: a page with `source:` copies an existing Markdown file, so you can keep guides
    and tutorials next to your API reference.

## Common workflow

```sh
pydoc-markdown --bootstrap mkdocs   # once: writes pydoc-markdown.yaml
pydoc-markdown --server --open      # live preview, re-renders when your code or source pages change
pydoc-markdown --build                     # render, then build the static site
pydoc-markdown --build --site-dir public   # ... into public/
```

Without `--site-dir`, the site goes to the generator's default (`site/` for MkDocs, `public/` for Hugo) inside the
renderer's output directory. `--server` and `--build` call the generator's own CLI, so `mkdocs` must be installed (with the theme you use). For
Hugo, a binary is downloaded from GitHub if `hugo` isn't on your `PATH`; configure this with the renderer's `get_hugo`
option.

## Pages

The `mkdocs` and `hugo` renderers take a `pages` tree. Each page either generates API docs (`contents`), copies an
existing file (`source`), or just groups `children`:

```yaml
renderer:
  type: mkdocs
  pages:
    - title: Home
      name: index
      source: README.md
    - title: API Documentation
      children:
        - title: Models
          contents: [my_project.models, my_project.models.*]
        - title: Utilities
          contents: [my_project.util.*]
          exclude: [my_project.util._compat]
  mkdocs_config:
    site_name: My Project
    theme: material
```

See [Configuration → Pages](configuration.md#pages) for all page options.

## MkDocs

The `mkdocs` renderer writes `mkdocs.yml` and the page tree into `output_directory` (default `build/docs`). Anything
under `mkdocs_config` is written to the generated `mkdocs.yml`, so you can set the theme, plugins and Markdown
extensions there; `nav` and `docs_dir` are generated from your `pages`. The server port defaults to 8000 and can be
changed with `server_port` or the `MKDOCS_PORT` environment variable.

## Hugo

The `hugo` renderer writes a Hugo site into `build_directory` (default `build/docs`). Hugo's own configuration goes
under `config`; a theme can be a name, a local path, or a Git URL to clone:

```yaml
renderer:
  type: hugo
  config:
    title: My Project
    theme: {clone_url: "https://github.com/alex-shpak/hugo-book.git"}
  content_directory: content/docs   # the "book" theme only shows pages under content/docs
  default_preamble: {menu: main}
  pages:
    - title: Home
      name: index
      source: README.md
    - title: API Documentation
      contents: [my_project.*]
```

Every generated file starts with a YAML front matter preamble made of `default_preamble` plus the page's own `preamble`.
To set `baseURL` per environment, see the [Hugo `baseURL` recipe](../recipes/hugo-base-url.md).

## Docusaurus

The `docusaurus` renderer doesn't use `pages`. It writes one Markdown file per module into
`<docs_base_path>/<relative_output_path>` (default `docs/reference`) and a `sidebar.json` you include from your
`sidebars.js`. Run it from the root of your Docusaurus project, then use Docusaurus' own tooling to serve and build.

```yaml
processors:
  - type: filter
    skip_empty_modules: true
  - type: smart
  - type: crossref
renderer:
  type: docusaurus
  docs_base_path: docs
  relative_output_path: reference
  relative_sidebar_path: sidebar.json
  sidebar_top_level_label: Reference
```

A complete example lives in [`examples/docusaurus`](https://github.com/NiklasRosenstein/pydoc-markdown/tree/develop/examples/docusaurus).

## Custom templates (experimental)

If none of the layouts above fit, the [`jinja2` renderer](../reference/renderers/jinja2.md) writes Markdown files from
your own [Jinja2](https://jinja.palletsprojects.com/) templates. Each entry under `produces` names an output file
(without `.md`) and the template variables; `module` and `modules` are replaced by the matching loaded modules:

```yaml
renderer:
  type: jinja2
  build_directory: build/docs
  renders:
    - template: templates/module.md.jinja2
      produces:
        api: {module: my_package}
```

```jinja title="templates/module.md.jinja2"
# {{ module.name }}

{% for cls in [module] | classes %}
## {{ cls.name }}

{{ cls.docstring.content if cls.docstring else "" }}
{% endfor %}
```

Templates are looked up relative to the current directory. Besides Jinja2's built-ins, templates can use the
`classes`, `functions`, `attrs`, `uid`, `indent`, `blockquote`, `first_line`, `format_arglist`,
`format_function_signature` and `describe` filters.

!!! warning

    The `jinja2` renderer is experimental: its options and the variables and filters available to templates may change
    in any release.
