# Deprecations and feature status

This page lists features that are deprecated, obsolete or experimental, and what to use instead. Removals only happen
in a major release.

## Supported

These features are actively maintained. Earlier announcements suggested otherwise, so to clear that up:

| Feature | Status |
| --- | --- |
| YAML / `pyproject.toml` configuration | **Supported.** Deprecated in 4.6.0, then undeprecated in 4.7.0. |
| `mkdocs`, `hugo` and `docusaurus` renderers | **Supported.** 4.6.0 said these would move to Novella; that plan was dropped. |
| `--server`, `--open`, `--build` | **Supported** for the `mkdocs` and `hugo` renderers. |

## Deprecated or obsolete

| Feature | Status | Use instead |
| --- | --- | --- |
| [Novella integration](guides/novella.md) (`@pydoc` / `\{@pylink}` tags) | **Deprecated; emits a `FutureWarning`.** Will be removed in a future major release. | A [configuration file](guides/configuration.md) with the `mkdocs` or `hugo` renderer. Include hand-written pages with `source:`. |
| `--py2` / `--py3` CLI flags | **Deprecated; has no effect and prints a warning.** They set the `python` loader's `parser.print_function` option, which docspec-python no longer reads, so Python 2 syntax such as the `print` statement can't be parsed. | Remove the flag. |
| `parser.print_function` option of the `python` loader | **Obsolete; has no effect.** See above. | Remove the option. |
| `pydoc-markdown[novella]` extra | **Doesn't exist.** Older docs told you to install it, and pip only prints a warning when it isn't found. | `pip install novella pydoc-markdown` (but see Novella above) |
| `Data` key in the Markdown renderer's `header_level_by_type` | **Deprecated alias** of `Variable`, kept for backwards compatibility. | `header_level_by_type: {Variable: …}` |
| `pydoc_markdown.util.pages.Page[T]` | **Deprecated alias** of `GenericPage[T]`, kept for compatibility with plugins written before 4.8.1. | `GenericPage[T]` |

## Experimental or legacy

| Feature | Status |
| --- | --- |
| [`jinja2` renderer](reference/renderers/jinja2.md) | **Experimental.** Its options and template API may change in any release. |
| [`crossref` processor](reference/processors.md) | **Limited.** Links only resolve with the `markdown`, `mkdocs`, `hugo` and `jinja2` renderers. Unresolved references become inline code. |
| `pydocmd` docstring style (`# Arguments` sections) | **Legacy, still supported.** Prefer Google, NumPy or reST style for new code; see [Docstrings](guides/docstrings.md). |
| `google` processor | **Supported**, but the `sphinx` processor with `style: GOOGLE` also parses Google docstrings, with a different implementation. |
