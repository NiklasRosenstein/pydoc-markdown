# Getting started

  [Novella]: https://niklasrosenstein.github.io/novella/

Starting with Pydoc-Markdown v4.6.0, you should configure your build using [Novella]. Note however, that Novella
is not installed directly with Pydoc-Markdown because it requires Python 3.8+ and for backwards compatibility with
the old build style prior to v4.7.0, Pydoc-Markdown remains 3.7 compatible.

You need to install Novella separetely or use the Pydoc-Markdown extra.

    $ pip install pydoc-markdown[novella]

## Configuration

A Novella build is configured using a `build.novella` script. In most cases you want to rely on a template provided
by Novella, such as the MkDocs template. Check out the Novella documentation to find what types of templates
are available [here](https://niklasrosenstein.github.io/novella/components/templates_/).

```py title="docs/build.novella"
template "mkdocs" {
  content_directory = "content"
}

action "preprocess-markdown" {
  use "pydoc"
}
```

What is happening here?

1. The `mkdocs` pipeline template is applied. The `content_directory` is the directory that contains your MkDocs
   source files. It will be copied to the temporary build location alongside the `mkdocs.yml` file. Note that your
   `build.novella` script should sit next two these files.

2. The `preprocess-markdown` action that is one of the actions created by the template is retrieved and configured
   further. We instruct it to make use of the `"pydoc"` plugin, which is implemented by Pydoc-Markdown and provides
   the `@pydoc` and `{@pylink}` tags.

!!! note

    * The `content/` directory is the default so it does not need to be set explicitly and it is sufficient to write
      `template "mkdocs"` (without an empty configuration block).
    
    * The `mkdocs` template will apply a default configuration delivered with Novella to your MkDocs configuration. If
      you don't want this, you can configure the `"mkdocs-update-config"` action to disable this. Note that you can
      also have no MkDocs configuration file and the template will create a default file for you.
    
    * The `pydoc` tag is implemented in {@pylink pydoc_markdown.novella.preprocessor.PydocTagPreprocessor}. Look it
      up to understand how it can be configured further.

    * The `pydoc` tag processor applies a heuristic to populate the default search path for your Python source
      code. If the directory in which the build is executed is called `docs` or `documentation`, it will default to
      `[ "../src", ".." ]`, otherwise it will default to `[ "src", "." ]`.

## Write some documentation

Before Pydoc-Markdown 4.6.0, a YAML configuration was used to describe the files to generate and their content. Now
with Novella as the preprocessor, you create those files leave special instructions to inject generated content.

For example, the `@cat` tag is useful to inject the content of another file.

```py title="docs/content/index.md"
# Welcome to my Project documentation!

\@cat ../../readme.md :with slice_lines = "2:"
```

The `@pydoc` tag is the piece provided by Pydoc-Markdown itself. It uses the {@pylink
pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer} to generate Markdown formatted API documentation of
the API object you specify.

```py title="docs/content/api.md"
# API Documentation

\@pydoc my_module.SomeClass
```

## Build the documentation

Change into the `docs/` directory where your `build.novella` script resides and invoke the Novella CLI. The MkDocs
template exposes some command-line arguments that you can pass through the CLI, one of which is the `--serve` option
that runs MkDocs in the server mode instead of building the documentation and writing it to disk.

    $ cd docs/
    $ novella --serve
    $ novella
