---
title: Home
---

# Pydoc-Markdown

Pydoc-Markdown generates Markdown API documentation for Python code. It **parses** your source with
[docspec](https://niklasrosenstein.github.io/python-docspec/) instead of importing it, so your package doesn't need to
be installed or importable, and the code may target any Python version.

* Converts Google, Sphinx/reST, NumPy, Epydoc and Pydoc-Markdown-style docstrings to Markdown.
* Picks up docstrings for variables (a `#:` comment block before, or a string literal after, the assignment).
* Turns references such as `#OtherClass` into links.
* Writes a single Markdown file, or a page tree for MkDocs, Hugo or Docusaurus.
* Adds "view source" links for GitHub, GitLab, Gitea, Bitbucket or any custom Git host.

## Pick a workflow

Pydoc-Markdown can be driven from a configuration file or from Python. Both share the same loaders, processors and
renderers.

| Workflow | Use it when | Start here |
| --- | --- | --- |
| **Configuration file** (`pydoc-markdown.yaml` or `pyproject.toml`) | You want one command that writes Markdown, or a whole MkDocs/Hugo/Docusaurus site, from a list of pages. | [Quickstart](getting-started/quickstart.md), then [Configuration](guides/configuration.md) |
| **Python API** | You call Pydoc-Markdown from your own build script. | [Python API](guides/python-api.md) |

If you are unsure, start with the configuration file. The [Novella integration](guides/novella.md) (`@pydoc` tags)
is deprecated; see [Deprecations](deprecations.md).

## Where to go next

* **[Installation](getting-started/installation.md)** and **[Quickstart](getting-started/quickstart.md)**: your first
  generated page in a few minutes.
* **Guides**: [configuration](guides/configuration.md), [docstring styles](guides/docstrings.md),
  [static site generators](guides/static-site-generators.md), [source links](guides/source-links.md).
* **Reference**: every [CLI option](reference/cli.md) and every option of every
  [loader](reference/loaders.md), [processor](reference/processors.md), renderer and
  [source linker](reference/source-linkers.md).
* **[Deprecations](deprecations.md)**: what is on its way out and what to use instead.
