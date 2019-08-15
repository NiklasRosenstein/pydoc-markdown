# Table of Contents

  * [pydoc\_markdown](#pydoc_markdown)
    * [\_\_author\_\_](#pydoc_markdown.__author__)
    * [\_\_version\_\_](#pydoc_markdown.__version__)
  * [pydoc\_markdown.contrib](#pydoc_markdown.contrib)
  * [pydoc\_markdown.contrib.loaders](#pydoc_markdown.contrib.loaders)
  * [pydoc\_markdown.contrib.loaders.python](#pydoc_markdown.contrib.loaders.python)
    * [dedent\_docstring](#pydoc_markdown.contrib.loaders.python.dedent_docstring)
    * [find](#pydoc_markdown.contrib.loaders.python.find)
    * [parse\_to\_ast](#pydoc_markdown.contrib.loaders.python.parse_to_ast)
    * [parse\_file](#pydoc_markdown.contrib.loaders.python.parse_file)
    * [Parser](#pydoc_markdown.contrib.loaders.python.Parser)
    * [ListScanner](#pydoc_markdown.contrib.loaders.python.ListScanner)
    * [PythonLoaderConfig](#pydoc_markdown.contrib.loaders.python.PythonLoaderConfig)
    * [PythonLoader](#pydoc_markdown.contrib.loaders.python.PythonLoader)
  * [pydoc\_markdown.contrib.processors](#pydoc_markdown.contrib.processors)
  * [pydoc\_markdown.contrib.processors.filter](#pydoc_markdown.contrib.processors.filter)
    * [FilterProcessorConfiguration](#pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration)
    * [FilterProcessor](#pydoc_markdown.contrib.processors.filter.FilterProcessor)
  * [pydoc\_markdown.contrib.processors.pydocmd](#pydoc_markdown.contrib.processors.pydocmd)
    * [PydocmdProcessorConfig](#pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessorConfig)
    * [PydocmdProcessor](#pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor)
  * [pydoc\_markdown.contrib.processors.sphinx](#pydoc_markdown.contrib.processors.sphinx)
    * [SphinxProcessorConfig](#pydoc_markdown.contrib.processors.sphinx.SphinxProcessorConfig)
    * [SphinxProcessor](#pydoc_markdown.contrib.processors.sphinx.SphinxProcessor)
  * [pydoc\_markdown.contrib.renderers](#pydoc_markdown.contrib.renderers)
  * [pydoc\_markdown.contrib.renderers.markdown](#pydoc_markdown.contrib.renderers.markdown)
    * [MarkdownRendererConfig](#pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig)
    * [MarkdownRenderer](#pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer)
  * [pydoc\_markdown.contrib.renderers.mkdocs](#pydoc_markdown.contrib.renderers.mkdocs)
    * [MkDocsRendererConfig](#pydoc_markdown.contrib.renderers.mkdocs.MkDocsRendererConfig)
    * [MkDocsRenderer](#pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer)
  * [pydoc\_markdown.interfaces](#pydoc_markdown.interfaces)
    * [Configurable](#pydoc_markdown.interfaces.Configurable)
    * [Loader](#pydoc_markdown.interfaces.Loader)
    * [LoaderError](#pydoc_markdown.interfaces.LoaderError)
    * [Processor](#pydoc_markdown.interfaces.Processor)
    * [Renderer](#pydoc_markdown.interfaces.Renderer)
    * [load\_implementation](#pydoc_markdown.interfaces.load_implementation)
  * [pydoc\_markdown.main](#pydoc_markdown.main)
    * [PydocMarkdownConfig](#pydoc_markdown.main.PydocMarkdownConfig)
    * [PydocMarkdown](#pydoc_markdown.main.PydocMarkdown)
    * [main](#pydoc_markdown.main.main)
  * [pydoc\_markdown.reflection](#pydoc_markdown.reflection)
    * [Location](#pydoc_markdown.reflection.Location)
    * [Object](#pydoc_markdown.reflection.Object)
    * [Module](#pydoc_markdown.reflection.Module)
    * [Class](#pydoc_markdown.reflection.Class)
    * [Function](#pydoc_markdown.reflection.Function)
    * [Data](#pydoc_markdown.reflection.Data)
    * [Decorator](#pydoc_markdown.reflection.Decorator)
    * [Argument](#pydoc_markdown.reflection.Argument)
    * [Expression](#pydoc_markdown.reflection.Expression)
    * [ModuleGraph](#pydoc_markdown.reflection.ModuleGraph)
  * [pydoc\_markdown.utils](#pydoc_markdown.utils)
    * [import\_object](#pydoc_markdown.utils.import_object)
    * [load\_entry\_point](#pydoc_markdown.utils.load_entry_point)

<h1 id="pydoc_markdown"><code>pydoc_markdown</code></h1>

-*- coding: utf8 -*-
Copyright (c) 2019 Niklas Rosenstein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

<h2 id="pydoc_markdown.__author__"><code>__author__</code></h2>

```
__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
```


<h2 id="pydoc_markdown.__version__"><code>__version__</code></h2>

```
__version__ = '3.0.0'
```


<h1 id="pydoc_markdown.contrib"><code>pydoc_markdown.contrib</code></h1>


<h1 id="pydoc_markdown.contrib.loaders"><code>pydoc_markdown.contrib.loaders</code></h1>


<h1 id="pydoc_markdown.contrib.loaders.python"><code>pydoc_markdown.contrib.loaders.python</code></h1>

-*- coding: utf8 -*-
Copyright (c) 2019 Niklas Rosenstein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

<h2 id="pydoc_markdown.contrib.loaders.python.dedent_docstring"><code>dedent_docstring()</code></h2>

```
dedent_docstring(s)
```


<h2 id="pydoc_markdown.contrib.loaders.python.find"><code>find()</code></h2>

```
find(predicate, iterable)
```


<h2 id="pydoc_markdown.contrib.loaders.python.parse_to_ast"><code>parse_to_ast()</code></h2>

```
parse_to_ast(code, filename)
```

Parses the string *code* to an AST with `lib2to3`.

<h2 id="pydoc_markdown.contrib.loaders.python.parse_file"><code>parse_file()</code></h2>

```
parse_file(code, filename, module_name=None)
```

Creates a reflection of the Python source in the string *code*.

<h2 id="pydoc_markdown.contrib.loaders.python.Parser"><code>Parser</code> Objects</h2>

A helper class that parses a Python AST to turn it into objects of the
[[pydoc_markdown.reflection]] module. Extracts docstrings from functions
and single-line comments.

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse"><code>Parser.parse()</code></h3>

```
Parser.parse(self, ast, filename, module_name=None)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_declaration"><code>Parser.parse_declaration()</code></h3>

```
Parser.parse_declaration(self, parent, node, decorators=None)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_statement"><code>Parser.parse_statement()</code></h3>

```
Parser.parse_statement(self, parent, stmt)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_decorator"><code>Parser.parse_decorator()</code></h3>

```
Parser.parse_decorator(self, node)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_funcdef"><code>Parser.parse_funcdef()</code></h3>

```
Parser.parse_funcdef(self, parent, node, is_async, decorators)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_parameters"><code>Parser.parse_parameters()</code></h3>

```
Parser.parse_parameters(self, parameters)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_classdef"><code>Parser.parse_classdef()</code></h3>

```
Parser.parse_classdef(self, parent, node, decorators)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.location_from"><code>Parser.location_from()</code></h3>

```
Parser.location_from(self, node)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_return_annotation"><code>Parser.get_return_annotation()</code></h3>

```
Parser.get_return_annotation(self, node)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_most_recent_prefix"><code>Parser.get_most_recent_prefix()</code></h3>

```
Parser.get_most_recent_prefix(self, node)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_docstring_from_first_node"><code>Parser.get_docstring_from_first_node()</code></h3>

```
Parser.get_docstring_from_first_node(self, parent, module_level=False)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_statement_docstring"><code>Parser.get_statement_docstring()</code></h3>

```
Parser.get_statement_docstring(self, node)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_hashtag_docstring_from_prefix"><code>Parser.get_hashtag_docstring_from_prefix()</code></h3>

```
Parser.get_hashtag_docstring_from_prefix(self, node)
```


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.prepare_docstring"><code>Parser.prepare_docstring()</code></h3>

```
Parser.prepare_docstring(self, s)
```

TODO @NiklasRosenstein handle u/f prefixes of string literal?

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.nodes_to_string"><code>Parser.nodes_to_string()</code></h3>

```
Parser.nodes_to_string(self, nodes)
```

Converts a list of AST nodes to a string.

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.name_to_string"><code>Parser.name_to_string()</code></h3>

```
Parser.name_to_string(self, node)
```


<h2 id="pydoc_markdown.contrib.loaders.python.ListScanner"><code>ListScanner</code> Objects</h2>

```
ListScanner.__init__(self, lst, index=0)
```

A helper class to navigate through a list. This is useful if you would
usually iterate over the list by index to be able to acces the next
element during the iteration.

Example:

```py
scanner = ListScanner(lst)
for value in scanner.safe_iter():
  if some_condition(value):
    value = scanner.advance()
```

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.__init__"><code>ListScanner.__init__()</code></h3>

```
ListScanner.__init__(self, lst, index=0)
```


<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.__bool__"><code>ListScanner.__bool__()</code></h3>

```
ListScanner.__bool__(self)
```


<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.__nonzero__"><code>__nonzero__</code></h3>

```
__nonzero__ = __bool__
```


<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.current"><code>ListScanner.current()</code></h3>

```
@property
ListScanner.current(self)
```

Returns the current list element.

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.can_advance"><code>ListScanner.can_advance()</code></h3>

```
ListScanner.can_advance(self)
```

Returns `True` if there is a next element in the list.

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.advance"><code>ListScanner.advance()</code></h3>

```
ListScanner.advance(self, expect=False)
```

Advances the scanner to the next element in the list. If *expect* is set
to `True`, an [[IndexError]] will be raised when there is no next element.
Otherwise, `None` will be returned.

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.safe_iter"><code>ListScanner.safe_iter()</code></h3>

```
ListScanner.safe_iter(self, auto_advance=True)
```

A useful generator function that iterates over every element in the list.
You may call [[advance()]] during the iteration to retrieve the next
element in the list within a single iteration.

If *auto_advance* is `True` (default), the function generator will
always advance to the next element automatically. If it is set to `False`,
[[advance()]] must be called manually in every iteration to ensure that
the scanner has advanced at least to the next element, or a
[[RuntimeError]] will be raised.

<h2 id="pydoc_markdown.contrib.loaders.python.PythonLoaderConfig"><code>PythonLoaderConfig</code> Objects</h2>

: A list of module or package names that this loader will search for and
: then parse. The modules are searched using the [[sys.path]] of the current
: Python interpreter, unless the [[search_path]] option is specified.

<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoaderConfig.modules"><code>modules</code></h3>

```
modules = Field([str])
```

: A list of module or package names that this loader will search for and
: then parse. The modules are searched using the [[sys.path]] of the current
: Python interpreter, unless the [[search_path]] option is specified.

<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoaderConfig.search_path"><code>search_path</code></h3>

```
search_path = Field([str], default=None)
```

: The module search path. If not specified, the current [[sys.path]] is
: used instead. If any of the elements contain a `*` (star) symbol, it
: will be expanded with [[sys.path]].

<h2 id="pydoc_markdown.contrib.loaders.python.PythonLoader"><code>PythonLoader</code> Objects</h2>

This implementation of the [[Loader]] interface parses Python modules and
packages. Which files are parsed depends on the configuration (see
[[PythonLoaderConfig]]).

<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoader.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>

```
CONFIG_CLASS = PythonLoaderConfig
```


<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoader.load"><code>PythonLoader.load()</code></h3>

```
PythonLoader.load(self, config, graph)
```


<h1 id="pydoc_markdown.contrib.processors"><code>pydoc_markdown.contrib.processors</code></h1>


<h1 id="pydoc_markdown.contrib.processors.filter"><code>pydoc_markdown.contrib.processors.filter</code></h1>

Provides a processor that implements various filter capabilities.

<h2 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration"><code>FilterProcessorConfiguration</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.expression"><code>expression</code></h3>

```
expression = Field(str, default=None)
```


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.documented_only"><code>documented_only</code></h3>

```
documented_only = Field(bool, default=False)
```


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.exclude_private"><code>exclude_private</code></h3>

```
exclude_private = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.exclude_special"><code>exclude_special</code></h3>

```
exclude_special = Field(bool, default=True)
```


<h2 id="pydoc_markdown.contrib.processors.filter.FilterProcessor"><code>FilterProcessor</code> Objects</h2>

The `filter` processor removes module and class members based on certain
criteria.

__Example__


```py
- type: filter
  expression: not name.startswith('_') and default()
```

<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessor.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>

```
CONFIG_CLASS = FilterProcessorConfiguration
```


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessor.process"><code>FilterProcessor.process()</code></h3>

```
FilterProcessor.process(self, config, graph)
```


<h1 id="pydoc_markdown.contrib.processors.pydocmd"><code>pydoc_markdown.contrib.processors.pydocmd</code></h1>

Provides the `PydocmdProcessor` class which converts the Pydoc-Markdown
highlighting syntax into Markdown.

<h2 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessorConfig"><code>PydocmdProcessorConfig</code> Objects</h2>


<h2 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor"><code>PydocmdProcessor</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>

```
CONFIG_CLASS = PydocmdProcessorConfig
```


<h3 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor.process"><code>PydocmdProcessor.process()</code></h3>

```
PydocmdProcessor.process(self, config, graph)
```


<h1 id="pydoc_markdown.contrib.processors.sphinx"><code>pydoc_markdown.contrib.processors.sphinx</code></h1>

Provides the `SphinxProcessor` that converts reST/Sphinx syntax to
markdown compatible syntax.

<h2 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessorConfig"><code>SphinxProcessorConfig</code> Objects</h2>


<h2 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessor"><code>SphinxProcessor</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessor.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>

```
CONFIG_CLASS = SphinxProcessorConfig
```


<h3 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessor.preprocess"><code>SphinxProcessor.preprocess()</code></h3>

```
SphinxProcessor.preprocess(self, root, node)
```


<h1 id="pydoc_markdown.contrib.renderers"><code>pydoc_markdown.contrib.renderers</code></h1>


<h1 id="pydoc_markdown.contrib.renderers.markdown"><code>pydoc_markdown.contrib.renderers.markdown</code></h1>

Implements a renderer that produces Markdown output.

<h2 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig"><code>MarkdownRendererConfig</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.filename"><code>filename</code></h3>

```
filename = Field(str, default=None)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.encoding"><code>encoding</code></h3>

```
encoding = Field(str, default='utf8')
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.html_headings"><code>html_headings</code></h3>

```
html_headings = Field(bool, default=False)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.code_headings"><code>code_headings</code></h3>

```
code_headings = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.code_lang"><code>code_lang</code></h3>

```
code_lang = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.descriptive_class_title"><code>descriptive_class_title</code></h3>

```
descriptive_class_title = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.add_method_class_prefix"><code>add_method_class_prefix</code></h3>

```
add_method_class_prefix = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.add_full_prefix"><code>add_full_prefix</code></h3>

```
add_full_prefix = Field(bool, default=False)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.sub_prefix"><code>sub_prefix</code></h3>

```
sub_prefix = Field(bool, default=False)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_code_block"><code>signature_code_block</code></h3>

```
signature_code_block = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_in_header"><code>signature_in_header</code></h3>

```
signature_in_header = Field(bool, default=False)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_with_def"><code>signature_with_def</code></h3>

```
signature_with_def = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_class_prefix"><code>signature_class_prefix</code></h3>

```
signature_class_prefix = Field(bool, default=False)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_expression_maxlength"><code>signature_expression_maxlength</code></h3>

```
signature_expression_maxlength = Field(int, default=100)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.render_toc"><code>render_toc</code></h3>

```
render_toc = Field(bool, default=True)
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.render_toc_title"><code>render_toc_title</code></h3>

```
render_toc_title = Field(str, default='Table of Contents')
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.toc_maxdepth"><code>toc_maxdepth</code></h3>

```
toc_maxdepth = Field(int, default=2)
```


<h2 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer"><code>MarkdownRenderer</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>

```
CONFIG_CLASS = MarkdownRendererConfig
```


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer.render"><code>MarkdownRenderer.render()</code></h3>

```
MarkdownRenderer.render(self, config, graph)
```


<h1 id="pydoc_markdown.contrib.renderers.mkdocs"><code>pydoc_markdown.contrib.renderers.mkdocs</code></h1>

Produces MkDocs structure.

<h2 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRendererConfig"><code>MkDocsRendererConfig</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRendererConfig.output_directory"><code>output_directory</code></h3>

```
output_directory = Field(str)
```


<h2 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer"><code>MkDocsRenderer</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>

```
CONFIG_CLASS = MkDocsRendererConfig
```


<h3 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer.render"><code>MkDocsRenderer.render()</code></h3>

```
MkDocsRenderer.render(self, modules)
```


<h1 id="pydoc_markdown.interfaces"><code>pydoc_markdown.interfaces</code></h1>

`pydoc_markdown.interfaces`
===========================

This module defines the interfaces that can to be implemented for
Pydoc-Markdown to implement custom loaders for documentation data,
processors or renderers.

<h2 id="pydoc_markdown.interfaces.Configurable"><code>Configurable</code> Objects</h2>

This interface represents an object that provides information on how it can
be configured via a YAML configuration file.

Implementations of this class can usually be loaded using the
[[load_implementation()]] function via the entrypoint specified on the
implementation class

<h3 id="pydoc_markdown.interfaces.Configurable.ENTRYPOINT_NAME"><code>ENTRYPOINT_NAME</code></h3>

```
ENTRYPOINT_NAME = None
```


<h3 id="pydoc_markdown.interfaces.Configurable.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>

```
CONFIG_CLASS = None
```


<h3 id="pydoc_markdown.interfaces.Configurable.config"><code>config</code></h3>

```
config = attr(default=None)
```


<h3 id="pydoc_markdown.interfaces.Configurable.make_instance"><code>Configurable.make_instance()</code></h3>

```
@staticattr
@classmethod
Configurable.make_instance(cls, impl_name, config)
```


<h2 id="pydoc_markdown.interfaces.Loader"><code>Loader</code> Objects</h2>

This interface describes an object that is capable of loading documentation
data. The location from which the documentation is loaded must be defined
with the configuration class.

<h3 id="pydoc_markdown.interfaces.Loader.ENTRYPOINT_NAME"><code>ENTRYPOINT_NAME</code></h3>

```
ENTRYPOINT_NAME = 'pydoc_markdown.interfaces.Loader'
```


<h3 id="pydoc_markdown.interfaces.Loader.load"><code>Loader.load()</code></h3>

```
Loader.load(self, config, graph)
```

Fill the [[ModuleGraph]].

<h2 id="pydoc_markdown.interfaces.LoaderError"><code>LoaderError</code> Objects</h2>


<h2 id="pydoc_markdown.interfaces.Processor"><code>Processor</code> Objects</h2>

A processor is an object that takes a `ModuleGraph` object as an input and
transforms it in an arbitrary way. This usually processes docstrings to
convert from various documentation syntaxes to plain Markdown.

<h3 id="pydoc_markdown.interfaces.Processor.ENTRYPOINT_NAME"><code>ENTRYPOINT_NAME</code></h3>

```
ENTRYPOINT_NAME = 'pydoc_markdown.interfaces.Processor'
```


<h3 id="pydoc_markdown.interfaces.Processor.process"><code>Processor.process()</code></h3>

```
Processor.process(self, config, graph)
```


<h2 id="pydoc_markdown.interfaces.Renderer"><code>Renderer</code> Objects</h2>

A renderer is an object that takes a `ModuleGraph` as an input and produces
output files or writes to stdout. It may also expose additional command-line
arguments. There can only be one renderer at the end of the processor chain.

Note that sometimes a renderer may need to perform some processing before
the render step. To keep the possibility open that a renderer may implement
generic processing that could be used without the actual renderering
functionality, `Renderer` is a subclass of `Processor`.

<h3 id="pydoc_markdown.interfaces.Renderer.ENTRYPOINT_NAME"><code>ENTRYPOINT_NAME</code></h3>

```
ENTRYPOINT_NAME = 'pydoc_markdown.interfaces.Renderer'
```


<h3 id="pydoc_markdown.interfaces.Renderer.process"><code>Renderer.process()</code></h3>

```
@default
Renderer.process(self, config, graph)
```


<h3 id="pydoc_markdown.interfaces.Renderer.render"><code>Renderer.render()</code></h3>

```
Renderer.render(self, config, graph)
```


<h2 id="pydoc_markdown.interfaces.load_implementation"><code>load_implementation()</code></h2>

```
load_implementation(interface, impl_name)
```

Loads an implementation of the specified *interface* (which must be a class
that provides an `ENTRYPOINT_NAME` attribute) that has the name *impl_name*.
The loaded class must implement *interface* or else a `RuntimeError` is
raised.

<h1 id="pydoc_markdown.main"><code>pydoc_markdown.main</code></h1>

Implements the pydoc-markdown CLI.

<h2 id="pydoc_markdown.main.PydocMarkdownConfig"><code>PydocMarkdownConfig</code> Objects</h2>


<h3 id="pydoc_markdown.main.PydocMarkdownConfig.loaders"><code>loaders</code></h3>

```
loaders = Field([_ExtensionConfig], default=list)
```


<h3 id="pydoc_markdown.main.PydocMarkdownConfig.processors"><code>processors</code></h3>

```
processors = Field([_ExtensionConfig], default=lambda: [_ExtensionConfig('pydocmd', {})])
```


<h3 id="pydoc_markdown.main.PydocMarkdownConfig.renderer"><code>renderer</code></h3>

```
renderer = Field(_ExtensionConfig, default=lambda: _ExtensionConfig('markdown', {}))
```


<h2 id="pydoc_markdown.main.PydocMarkdown"><code>PydocMarkdown</code> Objects</h2>

```
PydocMarkdown.__init__(self)
```

This class wraps all the functionality provided by the command-line.

<h3 id="pydoc_markdown.main.PydocMarkdown.__init__"><code>PydocMarkdown.__init__()</code></h3>

```
PydocMarkdown.__init__(self)
```


<h3 id="pydoc_markdown.main.PydocMarkdown.load_config"><code>PydocMarkdown.load_config()</code></h3>

```
PydocMarkdown.load_config(self, data)
```

Loads the configuration. *data* be a string pointing to a YAML file or
a dictionary.

<h3 id="pydoc_markdown.main.PydocMarkdown.load_module_graph"><code>PydocMarkdown.load_module_graph()</code></h3>

```
PydocMarkdown.load_module_graph(self)
```


<h3 id="pydoc_markdown.main.PydocMarkdown.process"><code>PydocMarkdown.process()</code></h3>

```
PydocMarkdown.process(self)
```


<h3 id="pydoc_markdown.main.PydocMarkdown.render"><code>PydocMarkdown.render()</code></h3>

```
PydocMarkdown.render(self)
```


<h2 id="pydoc_markdown.main.main"><code>main()</code></h2>

```
main(argv=None, prog=None)
```


<h1 id="pydoc_markdown.reflection"><code>pydoc_markdown.reflection</code></h1>

This module provides the abstract representation of a code library. It is
generalised and intended to be usable for any language.

<h2 id="pydoc_markdown.reflection.Location"><code>Location</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Object"><code>Object</code> Objects</h2>

```
Object.__init__(self, args, *,, ,, kwargs)
```


<h3 id="pydoc_markdown.reflection.Object.__init__"><code>Object.__init__()</code></h3>

```
Object.__init__(self, args, *,, ,, kwargs)
```


<h3 id="pydoc_markdown.reflection.Object.__repr__"><code>Object.__repr__()</code></h3>

```
Object.__repr__(self)
```


<h3 id="pydoc_markdown.reflection.Object.path"><code>Object.path()</code></h3>

```
Object.path(self, separator='.')
```


<h3 id="pydoc_markdown.reflection.Object.remove"><code>Object.remove()</code></h3>

```
Object.remove(self)
```


<h3 id="pydoc_markdown.reflection.Object.is_module"><code>Object.is_module()</code></h3>

```
Object.is_module(self)
```


<h3 id="pydoc_markdown.reflection.Object.is_class"><code>Object.is_class()</code></h3>

```
Object.is_class(self)
```


<h3 id="pydoc_markdown.reflection.Object.is_data"><code>Object.is_data()</code></h3>

```
Object.is_data(self)
```


<h3 id="pydoc_markdown.reflection.Object.is_function"><code>Object.is_function()</code></h3>

```
Object.is_function(self)
```


<h3 id="pydoc_markdown.reflection.Object.is_method"><code>Object.is_method()</code></h3>

```
Object.is_method(self)
```


<h3 id="pydoc_markdown.reflection.Object.visit"><code>Object.visit()</code></h3>

```
Object.visit(self, func, allow_mutation=False)
```


<h2 id="pydoc_markdown.reflection.Module"><code>Module</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Class"><code>Class</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Function"><code>Function</code> Objects</h2>


<h3 id="pydoc_markdown.reflection.Function.signature"><code>Function.signature()</code></h3>

```
@property
Function.signature(self)
```


<h3 id="pydoc_markdown.reflection.Function.signature_args"><code>Function.signature_args()</code></h3>

```
@property
Function.signature_args(self)
```


<h2 id="pydoc_markdown.reflection.Data"><code>Data</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Decorator"><code>Decorator</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Argument"><code>Argument</code> Objects</h2>


<h3 id="pydoc_markdown.reflection.Argument.POS"><code>POS</code></h3>

```
POS = 'pos'
```


<h3 id="pydoc_markdown.reflection.Argument.POS_REMAINDER"><code>POS_REMAINDER</code></h3>

```
POS_REMAINDER = 'pos_remainder'
```


<h3 id="pydoc_markdown.reflection.Argument.KW"><code>KW</code></h3>

```
KW = 'kw'
```


<h3 id="pydoc_markdown.reflection.Argument.KW_ONLY"><code>KW_ONLY</code></h3>

```
KW_ONLY = 'kw_only'
```


<h3 id="pydoc_markdown.reflection.Argument.KW_REMAINDER"><code>KW_REMAINDER</code></h3>

```
KW_REMAINDER = 'kw_remainder'
```


<h3 id="pydoc_markdown.reflection.Argument.__str__"><code>Argument.__str__()</code></h3>

```
Argument.__str__(self)
```


<h3 id="pydoc_markdown.reflection.Argument.format_arglist"><code>Argument.format_arglist()</code></h3>

```
@staticmethod
Argument.format_arglist(arglist)
```


<h2 id="pydoc_markdown.reflection.Expression"><code>Expression</code> Objects</h2>


<h3 id="pydoc_markdown.reflection.Expression.__str__"><code>Expression.__str__()</code></h3>

```
Expression.__str__(self)
```


<h2 id="pydoc_markdown.reflection.ModuleGraph"><code>ModuleGraph</code> Objects</h2>

```
ModuleGraph.__init__(self)
```

Represents a collection of `Module` objects.

<h3 id="pydoc_markdown.reflection.ModuleGraph.__init__"><code>ModuleGraph.__init__()</code></h3>

```
ModuleGraph.__init__(self)
```


<h3 id="pydoc_markdown.reflection.ModuleGraph.add_module"><code>ModuleGraph.add_module()</code></h3>

```
ModuleGraph.add_module(self, module)
```


<h3 id="pydoc_markdown.reflection.ModuleGraph.visit"><code>ModuleGraph.visit()</code></h3>

```
ModuleGraph.visit(self, func, allow_mutation=False)
```


<h1 id="pydoc_markdown.utils"><code>pydoc_markdown.utils</code></h1>

-*- coding: utf8 -*-
Copyright (c) 2019 Niklas Rosenstein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

<h2 id="pydoc_markdown.utils.import_object"><code>import_object()</code></h2>

```
import_object(name)
```


<h2 id="pydoc_markdown.utils.load_entry_point"><code>load_entry_point()</code></h2>

```
load_entry_point(group, name)
```

Returns the first entry point registered to the specified *group* that
matches the *name*. If multiple entry points are registered to that name,
an `EnvironmentError` is raised.

If no entry point with the specified *name* can be found, a `ValueError`
is raised instead.

