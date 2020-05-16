# Changelog

### v3.0.1 (unreleased)

* Added `--version` option to `pydoc-markdown` command.
* Added `-p,--package` option to the `pydoc-markdown` command (which overrides
  the `PythonLoader.packages` field).
* Added `PythonLoader.packages` which will load the specified Python package
  including all sub-packages and -modules.
* Changed behavior of `PythonLoader.modules`, which will now only load the
  module that was explictly specified and not sub-packages or modules (note
  that this also affects the `-m,--module` command-line option)

### v3.0.0 (2020-05-12)

* Initial release of Pydoc-markdown v3
