# Changelog

### v3.0.3 (unreleased)

* CLI
    * Rename `--watch-and-serve` to `--server`
    * Watch & serve mainloop now reloads the config file and does not open the
      browser on every reload
    * Fix `pydoc-markdown.yml` generated with `--bootstrap` (#118)
* `MarkdownRenderer`
    * Update default for `header_level_by_type` (2 -> 1 for modules, 3 -> 2 for classes)
    * Update default for `descriptive_class_title` (false -> true)
    * Added `content_directory` option (replaces hardcoded default `docs` -> `content`)
    * Renamed `clean_docs_directory_on_render` to `clean_render` and change default true -> false
* `MkdocsRenderer`
    * Changed `mkdocs_config` can be set to `null` (the renderer will refrain
      from writing a `mkdocs.yml` configuration file into the output directory)
* `PythonLoader`
    * Fix assignments with annotations being ignored by the parser (#115)

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
  module that was explicitly specified and not sub-packages or modules (note
  that this also affects the `-m,--module` command-line option)
* Dynamically lookup `MarkdownRenderer` configuration from the configured
  renderer such that renderers other than the `MarkdownRenderer` and
  `MkdocsRenderer` that embed a `MarkdownRenderer` can benefit from command-line
  level overrides like `--render-toc`

### v3.0.0 (2020-05-12)

* Initial release of Pydoc-markdown v3
