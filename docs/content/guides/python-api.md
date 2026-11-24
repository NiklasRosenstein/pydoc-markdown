# Python API

Everything the CLI does is available from Python, for use in your own build scripts.

## The full pipeline

{@pylink pydoc_markdown.PydocMarkdown} is the object a configuration file is loaded into. A fresh instance is
preconfigured with a `python` loader, the `filter`, `smart` and `crossref` processors and a `markdown` renderer:

```py
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

session = PydocMarkdown()
assert isinstance(session.loaders[0], PythonLoader)
session.loaders[0].search_path = ["src"]

modules = session.load_modules()
session.process(modules)

assert isinstance(session.renderer, MarkdownRenderer)
print(session.renderer.render_to_string(modules))
```

To start from a configuration file or dictionary instead, call `session.load_config("pydoc-markdown.yml")` before
loading modules, then `session.render(modules)` to run the configured renderer.

## Individual plugins

Plugins can also be used on their own. Each one must be initialized with a
{@pylink pydoc_markdown.interfaces.Context} first:

```py
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context

context = Context(directory=".")
loader = PythonLoader(search_path=["src"], packages=["my_package"])
processor = SmartProcessor()
renderer = MarkdownRenderer(render_module_header=False)
for plugin in (loader, processor, renderer):
    plugin.init(context)

modules = list(loader.load())
processor.process(modules, None)
print(renderer.render_to_string(modules))
```

!!! note

    Without a `filter` processor, every member is rendered, including private and undocumented ones.

## Writing a plugin

Loaders, processors, renderers and source linkers implement the interfaces in
[`pydoc_markdown.interfaces`](../reference/interfaces.md). To make a plugin available by `type` name in configuration
files, register it under the matching entry point group in your package's `pyproject.toml`:

```toml
[project.entry-points."pydoc_markdown.interfaces.Processor"]
my-processor = "my_package.pydoc:MyProcessor"
```

The groups are `pydoc_markdown.interfaces.Loader`, `.Processor`, `.Renderer` and `.SourceLinker`. Plugins are
dataclasses; their fields become the options in the configuration file.
