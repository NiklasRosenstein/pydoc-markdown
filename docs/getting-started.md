# Getting started

## Installation

Pydoc-Markdown can be installed from PyPI. It is recommended to use [Pipx][]
to avoid dependency clashes with other command-line tools that you may have
installed.

    $ pipx install 'pydoc-markdown>=3.0.0,<4.0.0'
    $ pydoc-markdown --version

## CLI Usage

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

Check out the [Configuration](../configuration) section for details on the file
structure.

> __Tip__: The `--bootstrap` and `--bootstrap-mkdocs` options can be used to
> write a template configuration file.
