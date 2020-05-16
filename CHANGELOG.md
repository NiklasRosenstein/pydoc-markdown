# Changelog

### v3.0.3 (unreleased)

* Rename `--watch-and-serve` to `--server`

### v3.0.2 (2020-05-16)

* Fix `NameError` in `MkdocsRenderer`

### v3.0.1 (2020-05-16)

* Added `--version` option to `pydoc-markdown` command.
* Added `-p,--package` option to the `pydoc-markdown` command (which overrides
  the `PythonLoader.packages` field).
* Added `pydoc_markdown.util.page` module
* Added `pydoc_markdown.__main__.RenderSession` class which makes the cli
  logic easier to maintain and re-use.
* Added hidden `MarkdownRenderer.fp` option.
* Added `PythonLoader.packages` which will load the specified Python package
  including all sub-packages and -modules.
* Changed behavior of `PythonLoader.modules`, which will now only load the
  module that was explictly specified and not sub-packages or modules (note
  that this also affects the `-m,--module` command-line option)
* Dynamically lookup `MarkdownRenderer` configuration from the configured
  renderer such that renderers other than the `MarkdownRenderer` and
  `MkdocsRenderer` that embed a `MarkdownRenderer` can benefit from command-line
  level overrides like `--render-toc`

### v3.0.0 (2020-05-12)

* Initial release of Pydoc-markdown v3
