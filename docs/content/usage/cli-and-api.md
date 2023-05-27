# CLI and API

If you only want to use Pydoc-Markdown to generate Markdown from Python code, but not use it for anything else
(such as interfacing with a static site generator), you can of course do that. You can make use of the {@pylink
pydoc_markdown.contrib.loaders.python.PythonLoader} and {@pylink pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer},
or more conveniently the {@pylink pydoc_markdown.PydocMarkdown} APIs, or use the CLI.

## CLI Example

The Pydoc-Markdown CLI accepts some options that can modify the default configuration (i.e. the Python loader and
Markdown renderer) and write the generated Markdown to stdout.

```sh
pydoc-markdown -I src -m package_name.module_name --render-toc > module_name.md
```

You can also supply a YAML configuration as a positional argument that will be treated the same way as if it
was loaded from a `pydoc-markdown.yml` file.

```sh
pydoc-markdown -m my_module '{
    renderer: {
      type: markdown,
      descriptive_class_title: false,
      render_toc: true
    }
  }' > my_module.md
```

## API Example

=== "Example 1"

    ```py
    from pydoc_markdown.interfaces import Context
    from pydoc_markdown.contrib.loaders.python import PythonLoader
    from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

    context = Context(directory='.')
    loader = PythonLoader(search_path=['src'])
    renderer = MarkdownRenderer(render_module_header=False)

    loader.init(context)
    renderer.init(context)

    modules = loader.load()
    print(renderer.render_to_string(modules))
    ```

    !!! note

        This does not include any filtering logic and will just render every member in your Python code.

=== "Example 2"

    ```py
    from pydoc_markdown import PydocMarkdown
    from pydoc_markdown.contrib.loaders.python import PythonLoader
    from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

    session = PydocMarkdown()  # Preconfigured with a PythonLoader, FilterProcessor, CrossRefProcess, SmartProcessor and MarkdownRenderer

    assert isinstance(session.loaders[0], PythonLoader)
    session.loaders[0].search_path = ["src"]

    assert isinstance(session.renderer, MarkdownRenderer)
    session.renderer.render_to_string(session.process(session.load_modules()))
    ```
