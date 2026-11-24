# Changelog

<!-- towncrier release notes start -->

## 4.8.2 (2023-06-26)

### Fixes

- Fix key aliases for `pre-render` and `post-render` keys in `Hooks` configuration (issue [#291](https://github.com/NiklasRosenstein/pydoc-markdown/issues/291), @NiklasRosenstein) ([#295](https://github.com/NiklasRosenstein/pydoc-markdown/pull/295))

## 4.8.1 (2023-06-21)

### Improvements

- Improve error message when no Pydoc Markdown configuration is found (@NiklasRosenstein) ([#293](https://github.com/NiklasRosenstein/pydoc-markdown/pull/293))

### Fixes

- Upgrade to Databind `^4.4.0` which fixes the "`ForwardRef` cannot be parameterized" error. (issue [#292](https://github.com/NiklasRosenstein/pydoc-markdown/issues/292), @NiklasRosenstein) ([#294](https://github.com/NiklasRosenstein/pydoc-markdown/pull/294))
- Fix `NoMatchingConverter` for `TypeHint(typing.List[~T_Page])` by making the `Page` type a concrete subclass of the old `Page` class now called `GenericPage`. This is needed to correctly define a recursive type that Databind can de/serialize. The `Page` type stays backwards compatible at runtime for cases when it is used as a generic (e.g. `class MyPage(Page[MyPage]):`) to not break existing code. (issue [#291](https://github.com/NiklasRosenstein/pydoc-markdown/issues/291), @NiklasRosenstein) ([#294](https://github.com/NiklasRosenstein/pydoc-markdown/pull/294))

### Tests

- Add unit tests to deserialize Mkdocs and Hugo example configuration. (@NiklasRosenstein) ([#294](https://github.com/NiklasRosenstein/pydoc-markdown/pull/294))

## 4.8.0 (2023-05-28)

### Improvements

- Upgrade from Databind `^1.5.0` to ^4.3.0`. This should not have any impact on the average Pydoc-Markdown user, however there may be some changes necessary for users that have been using the Pydoc-Markdown API beacuse of the changes to Databind between v1 and v4. However, these users should have pinned the major version of databind they're relying on, so this change is not considered breaking for Pydoc-Markdown. (@NiklasRosenstein) ([#289](https://github.com/NiklasRosenstein/pydoc-markdown/pull/289))

## 4.7.0 (2023-05-28)

### Improvements

- Change `PythonLoader.encoding` default value from `None` (system default) to `utf-8` (@NiklasRosenstein) ([#282](https://github.com/NiklasRosenstein/pydoc-markdown/pull/282))
- Support parsing all types of docstring formats that are supported by the `docstring_parser` module in `SphinxProcessor`, not just ReST (@hippalectryon-0) ([#282](https://github.com/NiklasRosenstein/pydoc-markdown/pull/282))
- Allow Pyyaml `^6.0` in addition to `^5.0` (@NiklasRosenstein) ([#287](https://github.com/NiklasRosenstein/pydoc-markdown/pull/287))
- Undeprecated YAML-based configuration for Pydoc-Markdown. (issue [#286](https://github.com/NiklasRosenstein/pydoc-markdown/issues/286), @NiklasRosenstein) ([#288](https://github.com/NiklasRosenstein/pydoc-markdown/pull/288))

### Fixes

- No longer HTML-escape text in Markdown code blocks. (@hippalectryon-0) ([#282](https://github.com/NiklasRosenstein/pydoc-markdown/pull/282))
- Fix codeblocks rendering to maintain indentation as per the original docstring. (issue [#169](https://github.com/NiklasRosenstein/pydoc-markdown/issues/169), @hippalectryon-0) ([#283](https://github.com/NiklasRosenstein/pydoc-markdown/pull/283))

### Documentation

- Update docs to inform user that `mkdocs` with `mkdocs-material` must be installed in Novella Usage guide. (issue [#270](https://github.com/NiklasRosenstein/pydoc-markdown/issues/270), @NiklasRosenstein)

## 4.6.4 (2022-11-13)

### Improvements

- add explicit compatibility with Novella 0.2.x (`>=0.1.10,<0.3.0`) (@NiklasRosenstein)

### Fixes

- fix interpreting Markdown in-document anchor links as cross references (issue [#274](https://github.com/NiklasRosenstein/pydoc-markdown/issues/274), @NiklasRosenstein)
- fix generated code for class signature with not base class and a metaclass parameter (issue [#272](https://github.com/NiklasRosenstein/pydoc-markdown/issues/272), @NiklasRosenstein)

### Documentation

- Fix installation instructions using Pipx (#256) (issue [#256](https://github.com/NiklasRosenstein/pydoc-markdown/issues/256), @NiklasRosenstein)

## 4.6.3 (2022-03-13)

### Fixes

- fix subscript error for type annotation in Python <=3.8 (@NiklasRosenstein)

## 4.6.2 (2022-03-13)

### Fixes

- fix AttributeError when using a Git source linker with `use_branch` disabled (issue [#250](https://github.com/NiklasRosenstein/pydoc-markdown/issues/250), @NiklasRosenstein) ([#252](https://github.com/NiklasRosenstein/pydoc-markdown/issues/252))

### Hygiene

- remove unused functions that interact with Git since the same functionality from the `nr.utils.git` module is used instead now (@NiklasRosenstein) ([#252](https://github.com/NiklasRosenstein/pydoc-markdown/issues/252))

## 4.6.1 (2022-03-05)

### Fixes

- fix recognition of overwritten values in `MarkdownRenderer.header_level_by_type` (issue [#248](https://github.com/NiklasRosenstein/pydoc-markdown/issues/248), @NiklasRosenstein) ([#249](https://github.com/NiklasRosenstein/pydoc-markdown/pull/249))
- fix backwards compat of handling `"Data"` key in `MarkdownRenderer.header_level_by_type` when now it should be `"Variable"` (@NiklasRosenstein) ([#249](https://github.com/NiklasRosenstein/pydoc-markdown/pull/249))

## 4.6.0 (2022-03-02)

### Breaking changes

- remove `MarkdownRenderer.render_to_stream()` from public api (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))

### Features

- add `pydoc_markdown.interfaces.SingleObjectRenderer` and use it in Novella `@pydoc` tag processor (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))
- add `ApiSuite` class and `ResolverV2` which is used by the new `@pydoc` tag preprocessor when using Novella (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))
- `MarkdownReferenceResolver` now implements the new `ResolverV2` interface and can resolve references globally (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))
- `CrossRefProcessor` now accepts a `resolver_v2` argument to use instead of the `resolver` object passed through the `Processor` API (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))
- bring back formatting function, class and variable signatures with YAPF. (Tagging @lgeiger as the author because he was the original author of the feature in a previous version of Pydoc-Markdown, see https://github.com/NiklasRosenstein/pydoc-markdown/pull/78) (issue [#244](https://github.com/NiklasRosenstein/pydoc-markdown/issues/244), @lgeiger) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))

### Improvements

- do not render link to source for modules in `MarkdownRenderer` (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))
- Git source linkers now fall back to the SHA if the current branch is invalid (e.g. in a detached HEAD state) and logs a warning (@NiklasRosenstein)

### Fixes

- fix forwarding of `PluginBase.init()` calls to sub-plugins in unittests and `DocusaurusRenderer` (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))

### Documentation

- docusaurus: Update `plugin-content-docs` config for docusarus@beta to not exclude files and folders with underscores. (issue [#189](https://github.com/NiklasRosenstein/pydoc-markdown/issues/189), @chrisstetter) ([#235](https://github.com/NiklasRosenstein/pydoc-markdown/pull/235))

### Hygiene

- remove `MarkdownRenderer.classdef_render_init_signature_if_needed` option because it never worked to begin with (@NiklasRosenstein) ([#245](https://github.com/NiklasRosenstein/pydoc-markdown/pull/245))

## 4.5.1 (2022-02-28)

### Fixes

- hugo: Hugo now respects the baseUrl option @Heiss (@NiklasRosenstein)
- hugo: Adds Apple Silicon to Hugo's recognized architectures. (@MilesCranmer)
- databind >1.4.0 changed Location.format() (issue [#246](https://github.com/NiklasRosenstein/pydoc-markdown/issues/246), @NiklasRosenstein)

### Documentation

- docusaurus: Update `plugin-content-docs` config for docusarus@beta to not exclude files and folders with underscores. (issue [#189](https://github.com/NiklasRosenstein/pydoc-markdown/issues/189), @chrisstetter)

## 4.5.0 (2021-12-12)

### Features

- MarkdownRenderer: Add `render_page_title` option. (issue [#214](https://github.com/NiklasRosenstein/pydoc-markdown/issues/214), issue [#216](https://github.com/NiklasRosenstein/pydoc-markdown/issues/216), @t6847kimo)
- git: Git source linkers now have a `use_branch` option to use the current branch name instead of the current commit SHA when generating links to the source code (issue [#218](https://github.com/NiklasRosenstein/pydoc-markdown/issues/218), @NiklasRosenstein)

## 4.4.0 (2021-12-12)

### Features

- HugoRenderer: add `serverURL` and `serverPort` options to `$.renderer.config` block to allow overwriting the URL where the local Hugo server serves from (issue [#202](https://github.com/NiklasRosenstein/pydoc-markdown/issues/202), issue [#231](https://github.com/NiklasRosenstein/pydoc-markdown/issues/231), @melMass)
- add `GitlabSourceLinker` class (entrypoint name: `gitlab`). @Heiss (@NiklasRosenstein)
- MarkdownRenderer: add `render_typehint_in_data_header` option to `MarkdownRenderer` (issue [#229](https://github.com/NiklasRosenstein/pydoc-markdown/issues/229), @NiklasRosenstein)

### Fixes

- Sphinx processor now triggers when `:arg` or other Sphinx keywords are encountered in a docstring (issue [#221](https://github.com/NiklasRosenstein/pydoc-markdown/issues/221), @NiklasRosenstein)
- sphinx_processor: Fix multi-line parameter sphinx docstring rendering issue by switching to docstring-parser to parse the docstrings. @gmarks2149 (issue [#195](https://github.com/NiklasRosenstein/pydoc-markdown/issues/195), @NiklasRosenstein)
- Fix configuration generated with `--bootstrap mkdocs` (issue [#230](https://github.com/NiklasRosenstein/pydoc-markdown/issues/230), @gethvi)
- MarkdownRenderer: no longer escape markdown in headers when `html_headers` is enabled (used to result in additional backslashes when interpreted by most Markdown to HTML renderers) (@NiklasRosenstein)

### Tests

- Refactor sphinx processor tests and add new test for param keyword only. Fixes minor issue with argument only docstring. @gmarks2149 (@NiklasRosenstein)

## 4.3.2 (2021-09-04)

### Fixes

- minimum `click` version is `7.1`, allow also `8.x` (@NiklasRosenstein)

## 4.3.1 (2021-09-01)

### Fixes

- Calling pydoc-markdown with `--render-toc` option causes an exception (issue [#213](https://github.com/NiklasRosenstein/pydoc-markdown/issues/213), @NiklasRosenstein)

## 4.3.0 (2021-08-28)

### Improvements

- change default configuration of `MarkdownRenderer` (`signature_with_vertical_bar = False` (many people seemed to dislike that) and `signature_with_def = True` (for consistency with the included `class` keyword for classes)) (@NiklasRosenstein)

### Fixes

- fix use of `docspec.ApiObject.path` after we migrated away from using deprecated `docspec.ReverseMap` (@NiklasRosenstein)

## 4.2.0 (2021-08-20)

### Features

- MarkdownRenderer: @melMass added the `MarkdownRenderer.add_module_prefix` option (issue [#199](https://github.com/NiklasRosenstein/pydoc-markdown/issues/199), @NiklasRosenstein)

### Improvements

- update template for `--bootstrap readthedocs` and related documentation (@NiklasRosenstein)

### Fixes

- HugoRenderer: Enable Hugo `markup.goldmark.renderer.unsafe` option by default (issue [#198](https://github.com/NiklasRosenstein/pydoc-markdown/issues/198), @NiklasRosenstein)
- MarkdownRenderer: Markdown renderer produces header anchors with `name` attribute instead of `id` (issue [#200](https://github.com/NiklasRosenstein/pydoc-markdown/issues/200), @NiklasRosenstein)
- fix `mkdocs` bootstrap configuration, update mkdocs and hugo bootstrap config to include example on how to select parts of the API docs (@NiklasRosenstein)

### Documentation

- switch Pydoc-Markdown to generated its docs with MkDocs (@NiklasRosenstein)
- add Jinja2 renderer documentation in generated docs (@NiklasRosenstein)

## 4.1.6 (2021-08-09)

### Fixes

- HugoRenderer: Restore old behaviour for `HugoConfig.additional_options`, which should be deserialized flat (i.e. it takes on any additional options in the same object that can not be mapped to any other fields of the config object) (@NiklasRosenstein)

## 4.1.5 (2021-08-04)

### Fixes

- fix import from `databind.core` (@NiklasRosenstein)

## 4.1.4 (2021-08-04)

### Improvements

- Use `tempfile` instead of `nr.fs` (@NiklasRosenstein)

### Fixes

- remove unused dependency on `nr.collections` (@NiklasRosenstein)

## 4.1.3 (2021-07-24)

### Fixes

- MarkdownRenderer: Remove zombie line that triggers error when using the Markdown renderer directly (issue [#196](https://github.com/NiklasRosenstein/pydoc-markdown/issues/196), @NiklasRosenstein)

## 4.1.2 (2021-07-23)

### Features

- Jinja2Renderer: add `blockquote` and `describe` built-in filters (@NiklasRosenstein)

### Fixes

- fix `--render-toc` option (@NiklasRosenstein)

## 4.1.1 (2021-07-22)

### Improvements

- Jinja2Renderer: added `format_function_signature` filter (@NiklasRosenstein)

## 4.1.0 (2021-07-22)

### Features

- Add `jinja2` renderer (@NiklasRosenstein)

### Improvements

- MarkdownRenderer: add MarkdownReferenceResolver helper class (@NiklasRosenstein)

### Fixes

- CrossrefProcessor: missing trailing characters for unresolved crossref (@NiklasRosenstein)

## 4.0.1 (2021-07-22)

### Fixes

- fix Python version classifiers (@NiklasRosenstein)

## 4.0.0 (2021-07-22)

### Breaking changes

- Migrate to `databind.core 1.x` and `databind.json 1.x` from `nr.databind.core` and `nr.databin.json` and
  uses of `nr.interface` are replaced with ABCs. If you developed plugins for Pydoc-Markdown, please follow
  the guide at https://pydoc-markdown.readthedocs.io/en/latest/docs/migrate-from-3x-to-4x/. (@NiklasRosenstein)

### Improvements

- Pydoc-Markdown now requires Python 3.7 or newer (before it was 3.6 or newer). This is due to `databind.core` having that minimum version requirement (@NiklasRosenstein)

### Fixes

- docusaurus: Insert an additional newline after header anchors (`<a id=".."></a>`) when `MarkdownRenderer.insert_header_anchors`
  is enabled to fix Docusaurus header rendering. (@NiklasRosenstein)
- unset `__PYENV_LAUNCHER__` environment variable for commands invoked via `$.hooks.pre-render` and `$.hooks.post-render` to avoid issues when the hook invokes a script installed into a different Python virtualenv than the virtualenv that is currently active in the terminal (@NiklasRosenstein)

## 3.14.0 (2021-07-19)

### Features

- add `MarkdownRenderer.signature_with_vertical_bar` option (contributed by @t6847kimo) (issue [#192](https://github.com/NiklasRosenstein/pydoc-markdown/issues/192), @NiklasRosenstein)

## 3.13.0 (2021-05-29)

### Improvements

- upgrade to `docspec-python~0.2.0` (@NiklasRosenstein)

## 3.12.1 (2021-05-21)

### Fixes

- add missing `dataclasses` dependency for Python 3.6 compatibility (@NiklasRosenstein)
- set minimum Python version in `package.yml` to `^3.6` (@NiklasRosenstein)

## 3.12.0 (2021-05-21)

### Features

- SphinxProcessor: parse `type` and `rtype` (issue [#157](https://github.com/NiklasRosenstein/pydoc-markdown/issues/157), @NiklasRosenstein)

## 3.11.0 (2021-05-20)

### Features

- Add support for getting configuration from pyproject.toml under the [tool.pydoc-markdown] table (@NiklasRosenstein)

### Fixes

- fix docstring in PydocmdPreprocessor (@NiklasRosenstein)

## 3.10.3 (2021-05-09)

### Fixes

- sort sidebar items in docusaurus (issue [#183](https://github.com/NiklasRosenstein/pydoc-markdown/issues/183), @NiklasRosenstein)
- replace backslashes with forward slashes in docusaurus sidebar (actually in 3.10.2) (issue [#129](https://github.com/NiklasRosenstein/pydoc-markdown/issues/129), @NiklasRosenstein)

## 3.10.1 (2021-04-02)

### Fixes

- fix code blocks indentation in `SphinxProcessor` (issue [#179](https://github.com/NiklasRosenstein/pydoc-markdown/issues/179), @NiklasRosenstein)

## 3.10.0 (2021-02-20)

### Features

- add `PythonLoader.encoding` option (@NiklasRosenstein)

## 3.9.0 (2020-12-15)

### Improvements

- bump `watchdog` dependency to `^1.0.0` (@NiklasRosenstein)

### Fixes

- Fix `IndexError` while processing short module path (by @g6123) (issue [#167](https://github.com/NiklasRosenstein/pydoc-markdown/issues/167), @NiklasRosenstein)

## 3.8.0 (2020-11-06)

### Features

- add new `bitbucket` source linker (@hkenny, #163) (@NiklasRosenstein)

## 3.7.0 (2020-11-05)

### Improvements

- FilterProcessor: Fix `NameError: name _check is not defined`, slightly alter behaviour of `FilterProcessor.expression` field` (issue [#161](https://github.com/NiklasRosenstein/pydoc-markdown/issues/161), @NiklasRosenstein)

## 3.6.1 (2020-11-03)

### Fixes

- Fix using `data_code_block` option in `MarkdownRenderer`, and add a unit test for it (issue [#160](https://github.com/NiklasRosenstein/pydoc-markdown/issues/160), @NiklasRosenstein)

## 3.6.0 (2020-10-28)

### Features

- Add `git` and `gitea` source linker (@tboulogne, #158) (@NiklasRosenstein)

### Improvements

- Update Docusaurus sidebar generation (@m-vdb, #156) (@NiklasRosenstein)

## 3.5.0 (2020-09-04)

### Features

- docusaurus: Add new `docusaurus` Renderer (contributed to by @m-vdb) (issue [#151](https://github.com/NiklasRosenstein/pydoc-markdown/issues/151), issue [#147](https://github.com/NiklasRosenstein/pydoc-markdown/issues/147), @NiklasRosenstein)
- filter: add `FilterProcessor.skip_empty_modules` option (@NiklasRosenstein)
- markdown: Add `MarkdownRenderer.render_module_header_template` and `.escape_html_in_docstring` options (@NiklasRosenstein)
- cli: Add `--bootstrap docusaurus` option (@NiklasRosenstein)

### Improvements

- markdown: Remove `MarkdownRenderer.fp` option, add `MarkdownRenderer.render_to_stream()` (@NiklasRosenstein)

## 3.4.0 (2020-08-31)

### Features

- mkdocs: add `server_port` option, treat `MKDOCS_PORT` environment variable if `server_port` option is not set (issue [#148](https://github.com/NiklasRosenstein/pydoc-markdown/issues/148), @NiklasRosenstein)

## 3.3.1 (2020-08-29)

### Fixes

- markdown: Fix "list" object has no attribute "values" in `MarkdownRenderer` (issue [#149](https://github.com/NiklasRosenstein/pydoc-markdown/issues/149), @NiklasRosenstein)

## 3.3.0 (2020-07-17)

### Features

- plugin types can now be resolved by their FQN (i.e. the absolute import name, such as `pydoc_markdown.contrib.loaders.python.PythonLoader`) in addition to their registered entrypoint name. (issue [#131](https://github.com/NiklasRosenstein/pydoc-markdown/issues/131), @NiklasRosenstein)
- add new `SourceLinker` interface (@NiklasRosenstein)
- add `GitHubSourceLinker` class (entrypoint name: `github`) (@NiklasRosenstein)
- markdown: add `MarkdownRenderer.source_linker`, `.source_position` and `.source_format` options (issue [#122](https://github.com/NiklasRosenstein/pydoc-markdown/issues/122), @NiklasRosenstein)
- implement YTT-like YAML preprocessing when the Pydoc-Markdown configuration is loaded (@NiklasRosenstein)

### Improvements

- cli: `-v,--verbose` and `-q,--quiet` flags are now countable (e.g. `-vv` will raise the logging verbosity to `DEBUG`) (@NiklasRosenstein)
- internal: Ensure consistency independent of the CWD from which Pydoc-Markdown is invoked as long as the same configuration file is used by introduce the `Context` object and the `init()` method for plugins. The `Context.directory` is set to the parent directory of the `pydoc-markdown.yml` configuration file. Plugins use that directory to interpret relative paths instead of the current working directory. (@NiklasRosenstein)

## 3.2.0.post1 (2020-07-15)

### Fixes

- packaging: add `$.readme` to `pydoc-markdown/package.yaml`, fixing the generated `setup.py` to include the `README.md` from the parent folder. (issue [#130](https://github.com/NiklasRosenstein/pydoc-markdown/issues/130), @NiklasRosenstein)

## 3.2.0 (2020-07-13)

### Features

- cli: add `--dump` and `--with-processors/--without-processors` options (@NiklasRosenstein)
- mkdocs: The `MkdocsRenderer.clean_render` option is enabled again by default, but instead of removing the whole `content_directory`, it will instead only remove files that it has previously generated (it will place a `.generated-files.txt` file in the `output_directory` for that). (@NiklasRosenstein)
- cli: add `MarkdownRenderer.classdef_with_decorators` and `MarkdownRenderer.signature_with_decorators` options (@NiklasRosenstein)
- Add new `HugoRenderer` (YAML type name `hugo`). (issue [#106](https://github.com/NiklasRosenstein/pydoc-markdown/issues/106), @NiklasRosenstein)
- smart-processor: now looks for a `@doc:fmt:<formatter_name>` string in the docstring, which can be used to override the style that is used in case the automatically detected style is incorrect (@NiklasRosenstein)
- api: Add new `Builder` interface that is used with the new `--build` and `--site-dir` options (@NiklasRosenstein)
- mkdocs: Implement `Builder` interface for `MkDocsRenderer` (@NiklasRosenstein)
- hugo: Implement `Builder` interface for `HugoRenderer` (@NiklasRosenstein)
- cli: Add new `--build` and `--site-dir` options as well as `--bootstrap readthedocs` (@NiklasRosenstein)
- add new `$.hooks.pre-render` and `$.hooks.post-render` options (issue [#112](https://github.com/NiklasRosenstein/pydoc-markdown/issues/112), @NiklasRosenstein)

### Improvements

- use `docspec` module instead of `pydoc_markdown.reflection` to represent API objects (@NiklasRosenstein)
- python: use `docspec-python` to load Python API objects (@NiklasRosenstein)
- crossref: warnings produced about references that cannot be resolved are now summarized in a single log-line (@NiklasRosenstein)
- With the removal of `pydoc_markdown.reflection`, the `ModuleGraph` class has also been removed and replaced by List[docspec.Module]` (@NiklasRosenstein)
- filter: Rename FilterProcessor.include_root_objects to .do_not_filter_modules (@NiklasRosenstein)
- change type signatures and some method names of interfaces in `pydoc_markdown.interfaces` (@NiklasRosenstein)
- utils: The `Page.filtered_modules()` method now warns if an element in `Page.contents` did not match an API object (@NiklasRosenstein)
- cli: remove `--bootstrap-mkdocs` in favor of `--bootstrap` option which now accepts an argument (@NiklasRosenstein)
- cli: the `--bootstrap` option now requires an argument, which must be either "base", "mkdocs" or "hugo" (new) (@NiklasRosenstein)
- mkdocs: generated `mkdocs.yml` now uses forward slashes for filenames on Windows system to increase portability (issue [#129](https://github.com/NiklasRosenstein/pydoc-markdown/issues/129), @NiklasRosenstein)

### Fixes

- markdown: the Markdown header level for methods is now correctly read from the "Method" key in `MarkdownRenderer.header_level_by_type` (issue [#121](https://github.com/NiklasRosenstein/pydoc-markdown/issues/121), @NiklasRosenstein)
- mkdocs: Fix error in MkDocs navigation generation if a page has no `source` and no `contents` (@NiklasRosenstein)

### Documentation

- add docstrings to classes defined in `pydoc_markdown.contrib.processors` (@NiklasRosenstein)
- The Pydoc-Markdown documentation is now available on Read the Docs (https://pydoc-markdown.readthedocs.io/en/latest/) (@NiklasRosenstein)

## 3.1.1 (2020-06-26)

### Improvements

- dependencies: bump dependency on `nr.databind.core` to `~0.0.18` to avoid picking up the bad `0.0.17` version (issue [#126](https://github.com/NiklasRosenstein/pydoc-markdown/issues/126), @NiklasRosenstein)

## 3.1.0 (2020-06-04)

### Features

- markdown: added `content_directory` option (replaces hardcoded default `docs` value, defaults to `content` now) (@NiklasRosenstein)

### Improvements

- cli: rename `--watch-and-serve` option to `--server` (@NiklasRosenstein)
- cli: watch and serve mainloop now reloads the config file and does not open the browser another time if it was already opened once. (@NiklasRosenstein)
- markdown: * change default for `header_level_by_type` (`2` to `1` for modules, `3` to `2` for classes).
  * change default for `descriptive_class_title` (`false` to `true`) (@NiklasRosenstein)
- markdown: renamed `clean_docs_directory_on_render` to `clean_render` and change the default from `true` to `false`. (@NiklasRosenstein)
- mkdocs: `mkdocs_config` option can now be set to `null` (the renderer will the refrain
  from writing a `mkdocs.yml` file into the output directory). (@NiklasRosenstein)

### Fixes

- cli: fix `pydoc-markdown.yml` generated with `--bootstrap` (issue [#118](https://github.com/NiklasRosenstein/pydoc-markdown/issues/118), @NiklasRosenstein)
- python: fix assignments with annotations being ignored by the parser (issue [#115](https://github.com/NiklasRosenstein/pydoc-markdown/issues/115), @NiklasRosenstein)

## 3.0.2 (2020-05-16)

### Fixes

- mkdocs: fix `NameError` in `MkdocsRenderer` (@NiklasRosenstein)

## 3.0.1 (2020-05-16)

### Features

- cli: added `--version` option (@NiklasRosenstein)
- cli: added `-p,--package` option (which overrides `PythonLoader.packages`) (@NiklasRosenstein)
- utils: added `pydoc_markdown.utils.page` module (@NiklasRosenstein)
- cli: added `RenderSession` class to `pydoc_markdown.main` module which makes the cli logic easier to maintain and re-use. (@NiklasRosenstein)
- markdown: added hidden `MarkdownRenderer.fp` option (@NiklasRosenstein)
- python: added `PythonLoader.packages` option (@NiklasRosenstein)

### Improvements

- python: changed behavior of `PythonLoader.modules` option (it will not only load the module that was explicitly specified and exclude any sub-modules, if applicable). (@NiklasRosenstein)
- cli: dynamically lookup `MarkdownRenderer` configuration from the renderer to support renderers other than `MarkdownRenderer` and `MkdocsRenderer` that supply a `markdown` field that is an instance of `MarkdownRenderer` (so they can be used with `--render-toc` as well). (@NiklasRosenstein)

## 3.0.0 (2020-05-12)

### Features

- Initial release of Pydoc-Markdown v3. (@NiklasRosenstein)
