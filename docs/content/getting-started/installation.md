# Installation

Pydoc-Markdown requires **Python 3.10 or newer** to run. The project you are documenting can target any Python
version, because Pydoc-Markdown never imports it.

## As a command-line tool

Install it into its own environment with [pipx](https://pipx.pypa.io/) or [uv](https://docs.astral.sh/uv/):

=== "pipx"

    ```sh
    pipx install pydoc-markdown
    ```

=== "uv"

    ```sh
    uv tool install pydoc-markdown
    ```

## As a project dependency

If your docs are built from your project's development environment, add Pydoc-Markdown there instead:

```sh
pip install pydoc-markdown
```

## With Novella

The [Novella integration](../guides/novella.md) is a plugin that Novella discovers automatically. Install
Pydoc-Markdown into the same environment as Novella:

=== "pipx"

    ```sh
    pipx install novella
    pipx inject novella pydoc-markdown
    ```

=== "pip"

    ```sh
    pip install novella pydoc-markdown
    ```

Pydoc-Markdown is tested with Novella `>=0.1.10,<0.3.0`.

## Static site generators

Pydoc-Markdown writes Markdown; it does not bundle a site generator. If you use the `mkdocs` renderer with `--server`
or `--build`, install [MkDocs](https://www.mkdocs.org/) (and your theme) yourself. The `hugo` renderer downloads a
Hugo binary automatically if none is on your `PATH`. See [Static site generators](../guides/static-site-generators.md).
