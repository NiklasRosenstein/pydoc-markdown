# Pydoc-Markdown

[![Python versions](https://img.shields.io/pypi/pyversions/pydoc-markdown?style=flat-square)](https://pypi.org/project/pydoc-markdown/)
[![PyPI version](https://img.shields.io/pypi/v/pydoc-markdown?style=flat-square)](https://pypi.org/project/pydoc-markdown/)

Generate Markdown API documentation for Python code — without importing it. Pydoc-Markdown parses your source with
[docspec][], converts Google, Sphinx, NumPy and Markdown-style docstrings to Markdown, and writes plain Markdown files
or pages for MkDocs, Hugo and Docusaurus.

> [!NOTE]
> This project is maintained on a best-effort basis. If you are building a site with MkDocs, also consider
> [mkdocstrings](https://mkdocstrings.github.io/).

## Quickstart

```sh
pipx install pydoc-markdown
pydoc-markdown -I src -p my_package --render-toc > api.md
```

For anything beyond a one-off, put the configuration in a file:

```sh
pydoc-markdown --bootstrap base   # writes pydoc-markdown.yml
pydoc-markdown                    # renders it
```

Pydoc-Markdown needs Python 3.10+ to run; the code you document can target any Python version.

## Documentation

**[niklasrosenstein.github.io/pydoc-markdown][docs]** — getting started, configuration, docstring styles, static site
generators, the [Novella][] integration, and the full plugin reference.

## Contributing

Contributions are welcome — see the [contribution guidelines][contrib]. Questions go to
[GitHub Discussions](https://github.com/NiklasRosenstein/pydoc-markdown/discussions).

**Used by** [CosmPy](https://docs.fetch.ai/CosmPy/),
[Haystack](https://docs.haystack.deepset.ai/reference/agent-api),
[envd](https://envd.tensorchord.ai/api/starlark/v0/config.html), [tqdm](https://tqdm.github.io/) and others — open a
pull request to add your project.

[contrib]: https://github.com/NiklasRosenstein/pydoc-markdown/blob/develop/.github/CONTRIBUTING.md
[docs]: https://niklasrosenstein.github.io/pydoc-markdown/
[docspec]: https://niklasrosenstein.github.io/python-docspec/
[Novella]: https://niklasrosenstein.github.io/novella/
