# Configuration

Pydoc-Markdown will read the configuration from a file called `pydoc-markdown.yml` (or `.yaml`)
from the current working directory. Usually you would place this file in your project's root
directory. The YAML configuration is pre-processed with a [YTT][]-like templating language.

The file contains of four main sections:

* `loaders`: A list of plugins that load API objects, for example from Python source files. The
  default configuration defines just a `python` loader.
* `processors`: A list of plugins that process API objects to modify their docstrings (e.g. to
  adapt them from a documentation format to Markdown or to remove items that should not be
  rendered into the documentation). The default configuration defines the `filter`, `smart` and
  `crossref` processors in that order.
* `renderer`: A plugin that produces the output files. The default configuration defines the
  `markdown` renderer (which by default will render a single file to stdout).
* `hooks`: Configuration for commands that will be executed before and after rendering.

## YAML Preprocessing

  [YTT]: https://get-ytt.io/

> *New in Pydoc-Markdown 3.3.0. See also `pydoc_markdown.util.ytemplate`*

Pydoc-Markdown performs very basic pre-processing on the YAML configuration before it is
deserialized. The format is similar to that of [YTT][], but supports only a subset of the
features and logic is interpreted as actual Python code.

Supportes preprocessing features:

* `def` blocks to define a Python function (requires an `end` keyword, encapsulating YAML
  code into the function definition is not supported)
* Value substitution

Check out the [Read the Docs/Hugo baseURL](../read-the-docs#hugo-baseurl) documentation for an
example.

## Loaders

(Todo. See Loaders section on the left)

## Processors

(Todo. See Processors section on the left)

## Renderer

(Todo. See Renderers section on the left)

## Hooks

Example:

```yml
hooks:
  pre-render:
  - generate-changelog >docs/CHANGELOG.md
```

Allows you to specify shell commands that will be execute before or after the render step.

__Available keys__

* `$.hooks.pre-render`
* `$.hooks.post-render`
