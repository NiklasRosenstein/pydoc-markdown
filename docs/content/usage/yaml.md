@anchor yaml-config
# YAML Configuration

Pydoc-Markdown can be configured with using via a YAML file. By default, the CLI will look for a file
called `pydoc-markdown.yaml` (or `.yml`) in the current working directory. (Note that the configuration
is not read from file when using the `-m,--module`, `-p,--package` and other options that are intended
for invoking Pydoc-Markdown without a configuration file).

> __Tip__: The `--bootstrap` and `--bootstrap-mkdocs` options can be used to write a template configuration file.

If you use the YAML configuration, the configuration file is pre-processed with a [YTT][]-like templating
language (see [YAML Preprocessing](#yaml-preprocessing)).

The configuration contains of four main sections:

* `loaders`: A list of plugins that load API objects, for example from Python source files. The
  default configuration defines just a `python` loader.
* `processors`: A list of plugins that process API objects to modify their docstrings (e.g. to
  adapt them from a documentation format to Markdown or to remove items that should not be
  rendered into the documentation). The default configuration defines the `filter`, `smart` and
  `crossref` processors in that order.
* `renderer`: A plugin that produces the output files. The default configuration defines the
  `markdown` renderer (which by default will render a single file to stdout).
* `hooks`: Configuration for commands that will be executed before and after rendering.

### YAML Example

```yaml
loaders:
- type: python
  search_path: [../src]
renderer:
  type: mkdocs
  pages:
  - title: API Documentation
    name: index
    contents:
    - school.*
```

### PyProject Example

```toml
[[tool.pydoc-markdown.loaders]]
type = "python"
search_path = [ "../src" ]

[tool.pydoc-markdown.renderer]
type = "mkdocs"

[[tool.pydoc-markdown.renderer.pages]]
title = "API Documentation"
name = "index"
contents = [ "school.*" ]
```

## YAML Preprocessing

  [YTT]: https://get-ytt.io/

> *New in Pydoc-Markdown 3.3.0. See also `pydoc_markdown.util.ytemplate`*

Pydoc-Markdown performs very basic pre-processing on the YAML configuration before it is
deserialized. The format is similar to that of [YTT][], but supports only a subset of the
features and logic is interpreted as actual Python code.

Supports preprocessing features:

* `def` blocks to define a Python function (requires an `end` keyword, encapsulating YAML
  code into the function definition is not supported)
* Value substitution

Check out the [Read the Docs/Hugo baseURL](../../examples/hugo/#hugo-baseurl) documentation for an
example.

## Loaders

Loaders are configured in the `$.loaders` section of the Pydoc-Markdown configuration file.
The key must be a list of loader definitions. Currently there is only the
[Python Loader](../api-documentation/loaders#pydoc_markdown.contrib.loaders.python.PythonLoader).

Example:

```yaml
loaders:
- type: loadertype1
  key: value
- type: loadertype2
```

If no loaders are specified, the Python loader is used by default.

## Processors

Similar to the Loaders, the `$.processors` section expects a list of processor definitions.
If no processors are defined, the `filter`, `smart` and `crossref` processors are used (in
that order). Many processors do not have any additional options.

Example:

```yaml
processors:
- type: filter
  documented_only: false
- type: smart
- type: crossref
```

## Renderer

The `$.renderer` defines the renderer to use when running `pydoc-markdown` without arguments.
Some renderers support the `--server` option, which allows a live-preview of the documentation.
The default renderer is the [Markdown renderer](../api-documentation/renderers/markdown) which
will print the result to the terminal.

Other renderers may produce files on disk in a layout that conforms with the static site generator
that they aim to support.

Example:

```yaml
renderer:
  type: mkdocs
  pages:
  - title: API Documentation
    name: index
    contents:
    - school.*
```

## Hooks

Example:

```yaml
hooks:
  pre-render:
  - generate-changelog >docs/CHANGELOG.md
```

Allows you to specify shell commands that will be execute before or after the render step.

__Available keys__

* `$.hooks.pre-render`
* `$.hooks.post-render`

## Testing your Configuration

You can test the configuration of your loaders using the `pydoc-markdown --dump` option. Combine
this with `docpspec -m --dump-tree` to get a full formatted list tree of all API objects that
Pydoc-Markdown has discovered, after applying all processors. You can disable processors by
adding the `--without-processors` function.

```
$ pydoc-markdown --dump | docspec -m --dump-tree
module school._class
| class Class
| | data topic
| | data teacher
module school._person
| class Person
| | data name
| | data age
module school._pupil
| class Pupil
[ ... ]
```
