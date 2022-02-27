# Plain

!!! note

    This section is severly lacking details. Sorry!

You can use the Pydoc-Markdown CLI to generate some plain Markdown content for your Python project.

    $ pydoc-markdown -I src -m package_name.module_name --render-toc > module_name.md

This uses the default configuration which consists of a `python` loader, the `filter`, `smart` and `crossref`
processors and the `markdown` renderer. A YAML payload can be passed to the CLI that will be applied on top
of the default configuration, allowing you to make small adjustments that are not exposed via CLI options.

    $ pydoc-markdown -m my_module '{
        renderer: {
          type: markdown,
          descriptive_class_title: false,
          render_toc: true
        }
      }' > my_module.md
