---
title: Novella
---

# Using the new Novella build backend

  [Novella]: https://niklasrosenstein.github.io/novella/

Starting with Pydoc-Markdown v4.6.0, [Novella] is the new backend for Pydoc-Markdown and future development will be
focused on improving the integration and to improve Novella itself. The [old-style Pydoc-Markdown configuration](./old-style.md)
will not see any feature development, but stay around for until at least the next major release.

!!! note

    __For previous users of Pydoc-Markdown__

    Documentation builds with Novella are slightly different from Pydoc-Markdown's original build process. In essence,
    it is an agnostic build system that operates in a separate build directory. Builtin tools allow you to copy files
    into the build directory from your project root and then process these files, allowing for the Novella Markdown
    preprocessor and its plugins to take effect.

    Pydoc-Markdown plugs into the preprocessing and replaces `@pydoc` and `@pylink` tags in the Markdown files with
    generate API documentation in Markdown format.

  [MkDocs]: https://www.mkdocs.org/

## How to use Pydoc-Markdown with Novella?

A Novella build is configured using a `build.novella` script. In almost any circumstance, relying on a template
build process will be sufficient, and in cases where it isn't, subsequent adjustments should alleviate any
shortcomings of the template's configurability.

__Example__

```py
template "mkdocs" {
  content_directory = "content/"
}

action "mkdocs-preprocess-markdown" {
  use "pydoc"
}
```

What is happening here?

1. The `mkdocs` pipeline template is applied. The `content_directory` is the directory that contains your MkDocs
   source files. It will be copied to the temporary build location alongside the `mkdocs.yml` file. Note that your
   `build.novella` script should sit next two these files.

2. An action named `mkdoc-preprocess-markdown` is recalled and its configuration is updated further. This action was
   created by the `mkdocs` template invoked above. We need to activate the `pydoc` processor plugin in order for
   `@pydoc` tags to be recognized in your Markdown files. 

!!! note

    * The `content/` directory is the default so it does not need to be set explicitly and it is sufficient to write
      `template "mkdocs"` (without an empty configuration block).
    
    * The `mkdocs` template will apply a default configuration delivered with Novella to your MkDocs configuration. If
      you don't want this, set `apply_default = False` inside the configuration block. Note that you can also have no
      MkDocs configuration file and the template will create a default file for you.
    
    * The `pydoc` tag is implemented in {@link pydoc:pydoc_markdown.novella.preprocessor}. Look it up to understand
      how it can be configured further.

    * The `pydoc` tag processor makes applies a heuristic to populate the default search path for your Python source
      code. If the directory in which the build is executed is called `docs` or `documentation`, it will default to
      `[ "../src", ".." ]`, otherwise it will default to `[ "src", "." ]`.

Now you can run Novella to build your site with MkDocs. The MkDocs template provides a `--serve` option which makes
the pipeline run `mkdocs serve` instead of `mkdocs build`. It also supports automatically rebuilding the pipeline if
a Markdown source file changes.

    $ novella

!!! note

    You need to install Pydoc-Markdown with the `novella` extra or install Novella separately for this to work.

        $ pip install pydoc-markdown[novella]
