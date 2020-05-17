# Getting started

## Installation

Pydoc-Markdown can be installed from PyPI. It is recommended to use [Pipx][]
to avoid dependency clashes with other command-line tools that you may have
installed.

    $ pipx install 'pydoc-markdown>=3.0.0,<4.0.0'
    $ pydoc-markdown --version

## Simple Usage

The Pydoc-Markdown CLI provides a few options that make it easy to generate
Markdown from a Python module or package.

    $ pydoc-markdown -m my_module --render-toc > my_module.md

This uses the default configuration which consists of a `python` loader,
the `filter`, `smart` and `crossref` processors and the `markdown` renderer.
A YAML payload can be passed to the CLI that will be applied on top of the
default configuration, allowing you to make small adjustments that are not
exposed via CLI options.

    $ pydoc-markdown -m my_module '{
        renderer: {
          type: markdown,
          descriptive_class_title: false,
          render_toc: true
        }
      }' > my_module.md

## YAML configuration

Pydoc-Markdown can be configured with using via a YAML file. By default,
the CLI will look for a file called `pydoc-markdown.yaml` (or `.yml`) in
the current working directory. (Note that the configuration is not read from
file when using the `-m,--module`, `-p,--package` and other options that
are intended for invoking Pydoc-Markdown without a configuration file).

The configuration consists of three main sections:

1. `loaders`: Defines the list of loaders used to load the API objects to document.
2. `processors`: Defines the list of processors that will be applied on the
   loaded API objects before rendering. Processors usually apply filtering
   and modify the docstrings to a more Markdown-suitable format (eg. to convert
   Sphinx or Google documentation syntax)
3. `renderer`: Defines the renderer that is responsible for writing the
   API objects to disk in Markdown format. Some renderers can be used with
   the `--server` option which allows you to live-preview the generated
   Markdown documentation in a browser.

> __Tip__: The `--bootstrap` and `--bootstrap-mkdocs` options can be used to
> write a template configuration file.

Pydoc-Markdown comes with a default loader for Python modules/packages based
on `lib2to3` as well as a couple of processors and renderers. Other Python
packages can registered additional Pydoc-Markdown plugins via entrypoints.

_Todo_: Link to documentation for available plugins.

## lib2to3 Quirks

Pydoc-Markdown doesn't execute your Python code but instead relies on the
`lib2to3` parser. This means it also inherits any quirks of `lib2to3`.

__List of known quirks__

* A function argument in Python 3 cannot be called `print` even though
  it is legal syntax
