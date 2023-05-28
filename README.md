# Pydoc-Markdown 📃

![Python versions](https://img.shields.io/pypi/pyversions/pydoc-markdown?style=for-the-badge)
[![Pypi version](https://img.shields.io/pypi/v/pydoc-markdown?style=for-the-badge)](https://pypi.org/project/pydoc-markdown/)

Pydoc-Markdown is a tool to create Python API documentation in Markdown format. Instead of executing your Python
code like so many other documentation tools, it parses it using [docspec][] instead.

[→ Go to the Documentation 📘][Documentation]

  [contrib]: https://github.com/NiklasRosenstein/pydoc-markdown/blob/develop/.github/CONTRIBUTING.md
  [docspec]: https://niklasrosenstein.github.io/docspec/
  [Documentation]: https://niklasrosenstein.github.io/pydoc-markdown/
  [MkDocs]: https://www.mkdocs.org/
  [Novella]: https://niklasrosenstein.github.io/novella/
  [Novella build backend]: https://niklasrosenstein.github.io/pydoc-markdown/usage/novella/

__Table of Contents__

* [Installation 📦](#installation-)
* [Features 🌟](#features-)
* [News 📢](#news-)
  * [4.7.0 (Undeprecating YAML configuration)](#470-undeprecating-yaml-configuration)
  * [4.6.0 (Novella integration)](#460-novella-integration)
* [Contributing to Pydoc-Markdown 🤝](#contributing-to-pydoc-markdown-)
* [Questions / Need help? 🤔](#questions--need-help-)
* [Projects using Pydoc-Markdown 📚](#projects-using-pydoc-markdown-)

### Installation 📦

You can install Pydoc-Markdown using Pipx:

    $ pipx install pydoc-markdown

If you plan on using the [Novella][] integration, you may want to install it as:

    $ pipx install novella
    $ pipx inject novella pydoc-markdown[novella]

You need at least Python 3.7 to run Pydoc-Markdown. The Python version compatibility of the package you are looking to
generate documentation for is irrelevant.

### Features 🌟

* Understands multiple documentation styles (Sphinx, Google, Pydoc-Markdown specific) and converts them to properly
  formatted Markdown
* Can parse docstrings for variables thanks to [docspec][] (`#:` block before or string literal after the statement)
* Generates links to other API objects per the documentation syntax (e.g. `#OtherClass` for the Pydoc-Markdown style)
* Configure the output using a YAML file or `pyProject.toml`, then you're only one command away to generate the
  documentation in Markdown format
* Or use [Novella][] to tightly integrate with static site generators like MkDocs and Hugo with with additional
  features such as Markdown pre-processing

### News 📢

#### 4.7.0 (Undeprecating YAML configuration)

Many users prefer the YAML configuration over the using [Novella][], which is why starting with __4.7.0__, the YAML
style configuration is officially un-deprecated and will continue to be supported.

#### 4.6.0 (Novella integration)

Starting with __4.6.0__, development focuses on integrating with [Novella][] and use it as a replacement for
tool-specific renderers thus far provided directly by Pydoc-Markdown (i.e. integrations with MkDocs, Hugo and
Docusuraus). Such integrations are/will be provided by Novella instead.

With the Novella integration, you can now place generated API content in Markdown format inline with your
existing Markdown documentation source files using `@pydoc` tags. Check out the [Documentation][] for more
information on how to use Pydoc-Markdown with Novella.

The old style of using Pydoc-Markdown with a YAML or PyProject configuration to generate files and kick off the
build is now deprecated but will be maintained for the foreseeable future (at least until the next major version
bump). It is strongly recommended to migrate your existing projects to using the Novella build backend.

### Contributing to Pydoc-Markdown 🤝

All contributions are welcome! Check out the [Contribution Guidelines][contrib].

### Questions / Need help? 🤔

Feel free to open a topic on [GitHub Discussions](https://github.com/NiklasRosenstein/pydoc-markdown/discussions)!

### Projects using Pydoc-Markdown 📚

An incomplete list of projects that use Pydoc-Markdown to generate their API documentation. Feel free to open a
pull request to add your project to this list!

* [CosmPy](https://docs.fetch.ai/CosmPy/)
* [haystack by deepset](https://docs.haystack.deepset.ai/reference/agent-api)
* [tensorchord/envd](https://envd.tensorchord.ai/api/starlark/v0/config.html)
* [tqdm](https://tqdm.github.io/)
