# Deprecations and feature status

This page lists features that are deprecated, obsolete or experimental, and what to use instead. None of them emit a
runtime warning yet. Where something will be removed, it happens in a major release at the earliest.

## Supported

These features are actively maintained. Earlier announcements suggested otherwise, so to clear that up:

| Feature | Status |
| --- | --- |
| YAML / `pyproject.toml` configuration | **Supported.** Deprecated in 4.6.0, then undeprecated in 4.7.0. |
| `mkdocs`, `hugo` and `docusaurus` renderers | **Supported.** 4.6.0 said these would move to Novella; they are still maintained and receive fixes. |
| `--server`, `--open`, `--build` | **Supported** for the `mkdocs` and `hugo` renderers. Always pass `--site-dir` together with `--build`. |
| [Novella integration](guides/novella.md) | **Supported.** An alternative to the configuration file, not its replacement. |

## Deprecated or obsolete

| Feature | Status | Use instead |
| --- | --- | --- |
| `--py2` / `--py3` CLI flags | **Obsolete; has no effect.** They set the `python` loader's `parser.print_function` option, which docspec-python no longer reads, so Python 2 syntax such as the `print` statement can't be parsed. Passing either flag also disables loading of the configuration file. | Remove the flag. |
| `parser.print_function` option of the `python` loader | **Obsolete; has no effect.** See above. | Remove the option. |
| `--bootstrap readthedocs` | **Outdated.** Generates a `.readthedocs.yml` that uses the `python.version` setting, which Read the Docs has removed, and the `readthedocs-custom-steps` workaround. | Write the file by hand as shown in the [Read the Docs recipe](recipes/readthedocs.md). |
| `pydoc-markdown[novella]` extra | **Doesn't exist.** Older docs told you to install it, and pip only prints a warning when it isn't found. | `pipx inject novella pydoc-markdown` |
| `Data` key in the Markdown renderer's `header_level_by_type` | **Deprecated alias** of `Variable`, kept for backwards compatibility. | `header_level_by_type: {Variable: …}` |
| `pydoc_markdown.util.pages.Page[T]` | **Deprecated alias** of `GenericPage[T]`, kept for compatibility with plugins written before 4.8.1. | `GenericPage[T]` |

## Experimental or legacy

| Feature | Status |
| --- | --- |
| [`jinja2` renderer](reference/renderers/jinja2.md) | **Experimental.** Its options and template API may change in any release. |
| [`crossref` processor](reference/processors.md) | **Limited.** Links only resolve with the `markdown`, `mkdocs`, `hugo` and `jinja2` renderers, and in Novella. Unresolved references become inline code. |
| `pydocmd` docstring style (`# Arguments` sections) | **Legacy, still supported.** Prefer Google, NumPy or reST style for new code; see [Docstrings](guides/docstrings.md). |
| `google` processor | **Supported**, but the `sphinx` processor with `style: GOOGLE` also parses Google docstrings, with a different implementation. |
