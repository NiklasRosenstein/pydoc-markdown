# Table of Contents

  * [pydoc\_markdown](#pydoc_markdown)
    * [\_\_author\_\_](#pydoc_markdown.__author__)
    * [\_\_version\_\_](#pydoc_markdown.__version__)
  * [pydoc\_markdown.interfaces](#pydoc_markdown.interfaces)
    * [Configurable](#pydoc_markdown.interfaces.Configurable)
    * [Loader](#pydoc_markdown.interfaces.Loader)
    * [LoaderError](#pydoc_markdown.interfaces.LoaderError)
    * [Processor](#pydoc_markdown.interfaces.Processor)
    * [Renderer](#pydoc_markdown.interfaces.Renderer)
    * [load\_implementation](#pydoc_markdown.interfaces.load_implementation)
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
  * [pydoc\_markdown.textdom](#pydoc_markdown.textdom)
    * [Node](#pydoc_markdown.textdom.Node)
    * [Text](#pydoc_markdown.textdom.Text)
    * [Reference](#pydoc_markdown.textdom.Reference)
  * [pydoc\_markdown.contrib](#pydoc_markdown.contrib)
  * [pydoc\_markdown.contrib.renderers](#pydoc_markdown.contrib.renderers)
  * [pydoc\_markdown.contrib.renderers.markdown](#pydoc_markdown.contrib.renderers.markdown)
    * [MarkdownRendererConfig](#pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig)
    * [MarkdownRenderer](#pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer)
  * [pydoc\_markdown.contrib.renderers.mkdocs](#pydoc_markdown.contrib.renderers.mkdocs)
    * [MkDocsRendererConfig](#pydoc_markdown.contrib.renderers.mkdocs.MkDocsRendererConfig)
    * [MkDocsRenderer](#pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer)
  * [pydoc\_markdown.contrib.processors](#pydoc_markdown.contrib.processors)
  * [pydoc\_markdown.contrib.processors.sphinx](#pydoc_markdown.contrib.processors.sphinx)
    * [SphinxProcessorConfig](#pydoc_markdown.contrib.processors.sphinx.SphinxProcessorConfig)
    * [SphinxProcessor](#pydoc_markdown.contrib.processors.sphinx.SphinxProcessor)
  * [pydoc\_markdown.contrib.processors.pydocmd](#pydoc_markdown.contrib.processors.pydocmd)
    * [PydocmdProcessorConfig](#pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessorConfig)
    * [PydocmdProcessor](#pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor)
  * [pydoc\_markdown.contrib.processors.filter](#pydoc_markdown.contrib.processors.filter)
    * [FilterProcessorConfiguration](#pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration)
    * [FilterProcessor](#pydoc_markdown.contrib.processors.filter.FilterProcessor)
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
  * [pydoc\_markdown.utils](#pydoc_markdown.utils)
    * [import\_object](#pydoc_markdown.utils.import_object)
    * [load\_entry\_point](#pydoc_markdown.utils.load_entry_point)
  * [pydoc\_markdown.main](#pydoc_markdown.main)
    * [PydocMarkdownConfig](#pydoc_markdown.main.PydocMarkdownConfig)
    * [PydocMarkdown](#pydoc_markdown.main.PydocMarkdown)
    * [main](#pydoc_markdown.main.main)

<h1 id="pydoc_markdown"><code>pydoc_markdown</code></h1>

Pydoc-markdown is an extensible framework for generating API documentation,
with a focus on Python source code and the Markdown output format.

<h2 id="pydoc_markdown.__author__"><code>__author__</code></h2>


<h2 id="pydoc_markdown.__version__"><code>__version__</code></h2>


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


<h3 id="pydoc_markdown.interfaces.Configurable.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>


<h3 id="pydoc_markdown.interfaces.Configurable.config"><code>config</code></h3>


<h3 id="pydoc_markdown.interfaces.Configurable.make_instance"><code>Configurable.make_instance(cls, impl_name, config)</code></h3>


<h2 id="pydoc_markdown.interfaces.Loader"><code>Loader</code> Objects</h2>

This interface describes an object that is capable of loading documentation
data. The location from which the documentation is loaded must be defined
with the configuration class.

<h3 id="pydoc_markdown.interfaces.Loader.ENTRYPOINT_NAME"><code>ENTRYPOINT_NAME</code></h3>


<h3 id="pydoc_markdown.interfaces.Loader.load"><code>Loader.load(self, config, graph)</code></h3>

Fill the [[ModuleGraph]].

<h2 id="pydoc_markdown.interfaces.LoaderError"><code>LoaderError</code> Objects</h2>


<h2 id="pydoc_markdown.interfaces.Processor"><code>Processor</code> Objects</h2>

A processor is an object that takes a `ModuleGraph` object as an input and
transforms it in an arbitrary way. This usually processes docstrings to
convert from various documentation syntaxes to plain Markdown.

<h3 id="pydoc_markdown.interfaces.Processor.ENTRYPOINT_NAME"><code>ENTRYPOINT_NAME</code></h3>


<h3 id="pydoc_markdown.interfaces.Processor.process"><code>Processor.process(self, config, graph)</code></h3>


<h2 id="pydoc_markdown.interfaces.Renderer"><code>Renderer</code> Objects</h2>

A renderer is an object that takes a `ModuleGraph` as an input and produces
output files or writes to stdout. It may also expose additional command-line
arguments. There can only be one renderer at the end of the processor chain.

Note that sometimes a renderer may need to perform some processing before
the render step. To keep the possibility open that a renderer may implement
generic processing that could be used without the actual renderering
functionality, `Renderer` is a subclass of `Processor`.

<h3 id="pydoc_markdown.interfaces.Renderer.ENTRYPOINT_NAME"><code>ENTRYPOINT_NAME</code></h3>


<h3 id="pydoc_markdown.interfaces.Renderer.process"><code>Renderer.process(self, config, graph)</code></h3>


<h3 id="pydoc_markdown.interfaces.Renderer.render"><code>Renderer.render(self, config, graph)</code></h3>


<h2 id="pydoc_markdown.interfaces.load_implementation"><code>load_implementation(interface, impl_name)</code></h2>

Loads an implementation of the specified *interface* (which must be a class
that provides an `ENTRYPOINT_NAME` attribute) that has the name *impl_name*.
The loaded class must implement *interface* or else a `RuntimeError` is
raised.

<h1 id="pydoc_markdown.reflection"><code>pydoc_markdown.reflection</code></h1>

This module provides the abstract representation of a code library. It is
generalised and intended to be usable for any language.

<h2 id="pydoc_markdown.reflection.Location"><code>Location</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Object"><code>Object</code> Objects</h2>


<h3 id="pydoc_markdown.reflection.Object.__init__"><code>Object.__init__(self, args, *,, ,, kwargs)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.__repr__"><code>Object.__repr__(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.path"><code>Object.path(self, separator='.')</code></h3>


<h3 id="pydoc_markdown.reflection.Object.remove"><code>Object.remove(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.is_module"><code>Object.is_module(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.is_class"><code>Object.is_class(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.is_data"><code>Object.is_data(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.is_function"><code>Object.is_function(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.is_method"><code>Object.is_method(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Object.visit"><code>Object.visit(self, func, allow_mutation=False)</code></h3>


<h2 id="pydoc_markdown.reflection.Module"><code>Module</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Class"><code>Class</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Function"><code>Function</code> Objects</h2>


<h3 id="pydoc_markdown.reflection.Function.signature"><code>Function.signature(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Function.signature_args"><code>Function.signature_args(self)</code></h3>


<h2 id="pydoc_markdown.reflection.Data"><code>Data</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Decorator"><code>Decorator</code> Objects</h2>


<h2 id="pydoc_markdown.reflection.Argument"><code>Argument</code> Objects</h2>


<h3 id="pydoc_markdown.reflection.Argument.POS"><code>POS</code></h3>


<h3 id="pydoc_markdown.reflection.Argument.POS_REMAINDER"><code>POS_REMAINDER</code></h3>


<h3 id="pydoc_markdown.reflection.Argument.KW"><code>KW</code></h3>


<h3 id="pydoc_markdown.reflection.Argument.KW_ONLY"><code>KW_ONLY</code></h3>


<h3 id="pydoc_markdown.reflection.Argument.KW_REMAINDER"><code>KW_REMAINDER</code></h3>


<h3 id="pydoc_markdown.reflection.Argument.__str__"><code>Argument.__str__(self)</code></h3>


<h3 id="pydoc_markdown.reflection.Argument.format_arglist"><code>Argument.format_arglist(arglist)</code></h3>


<h2 id="pydoc_markdown.reflection.Expression"><code>Expression</code> Objects</h2>


<h3 id="pydoc_markdown.reflection.Expression.__str__"><code>Expression.__str__(self)</code></h3>


<h2 id="pydoc_markdown.reflection.ModuleGraph"><code>ModuleGraph</code> Objects</h2>

Represents a collection of `Module` objects.

<h3 id="pydoc_markdown.reflection.ModuleGraph.__init__"><code>ModuleGraph.__init__(self)</code></h3>


<h3 id="pydoc_markdown.reflection.ModuleGraph.add_module"><code>ModuleGraph.add_module(self, module)</code></h3>


<h3 id="pydoc_markdown.reflection.ModuleGraph.visit"><code>ModuleGraph.visit(self, func, allow_mutation=False)</code></h3>


<h1 id="pydoc_markdown.textdom"><code>pydoc_markdown.textdom</code></h1>

Represent text as a tree-structured composed of groups, text and text
formatting containers (eg. links or code blocks).

<h2 id="pydoc_markdown.textdom.Node"><code>Node</code> Objects</h2>


<h3 id="pydoc_markdown.textdom.Node.__init__"><code>Node.__init__(self, children=None)</code></h3>


<h3 id="pydoc_markdown.textdom.Node.__repr__"><code>Node.__repr__(self)</code></h3>


<h3 id="pydoc_markdown.textdom.Node.__getitem__"><code>Node.__getitem__(self, index)</code></h3>


<h3 id="pydoc_markdown.textdom.Node.append"><code>Node.append(self, node)</code></h3>


<h3 id="pydoc_markdown.textdom.Node.unpack"><code>Node.unpack(self)</code></h3>

Returns the single child node if there is only one, otherwise returns
*self*. Recursively unpacks.

<h3 id="pydoc_markdown.textdom.Node.splittable"><code>Node.splittable(self)</code></h3>

Returns `True` if [[#split()]] can be called on the node. The default
implementation returns `True`.

<h3 id="pydoc_markdown.textdom.Node.split"><code>Node.split(self, char)</code></h3>

Splits the node by the specified character (usually used with line-feed)
and yields a sequence of [[Node]] objects.

<h3 id="pydoc_markdown.textdom.Node.default_render"><code>Node.default_render(self)</code></h3>


<h2 id="pydoc_markdown.textdom.Text"><code>Text</code> Objects</h2>


<h3 id="pydoc_markdown.textdom.Text.__init__"><code>Text.__init__(self, text)</code></h3>


<h3 id="pydoc_markdown.textdom.Text.__repr__"><code>Text.__repr__(self)</code></h3>


<h3 id="pydoc_markdown.textdom.Text.append"><code>Text.append(self, node)</code></h3>


<h3 id="pydoc_markdown.textdom.Text.split"><code>Text.split(self, char)</code></h3>


<h3 id="pydoc_markdown.textdom.Text.default_render"><code>Text.default_render(self)</code></h3>


<h2 id="pydoc_markdown.textdom.Reference"><code>Reference</code> Objects</h2>


<h3 id="pydoc_markdown.textdom.Reference.__init__"><code>Reference.__init__(self, name)</code></h3>


<h3 id="pydoc_markdown.textdom.Reference.__repr__"><code>Reference.__repr__(self)</code></h3>


<h3 id="pydoc_markdown.textdom.Reference.append"><code>Reference.append(self, node)</code></h3>


<h3 id="pydoc_markdown.textdom.Reference.splittable"><code>Reference.splittable(self)</code></h3>


<h3 id="pydoc_markdown.textdom.Reference.split"><code>Reference.split(self, char)</code></h3>


<h3 id="pydoc_markdown.textdom.Reference.default_render"><code>Reference.default_render(self)</code></h3>


<h1 id="pydoc_markdown.contrib"><code>pydoc_markdown.contrib</code></h1>


<h1 id="pydoc_markdown.contrib.renderers"><code>pydoc_markdown.contrib.renderers</code></h1>


<h1 id="pydoc_markdown.contrib.renderers.markdown"><code>pydoc_markdown.contrib.renderers.markdown</code></h1>

Implements a renderer that produces Markdown output.

<h2 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig"><code>MarkdownRendererConfig</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.filename"><code>filename</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.encoding"><code>encoding</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.html_headings"><code>html_headings</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.code_headings"><code>code_headings</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.code_lang"><code>code_lang</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.descriptive_class_title"><code>descriptive_class_title</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.add_method_class_prefix"><code>add_method_class_prefix</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.add_full_prefix"><code>add_full_prefix</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.sub_prefix"><code>sub_prefix</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_code_block"><code>signature_code_block</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_in_header"><code>signature_in_header</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_with_def"><code>signature_with_def</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_class_prefix"><code>signature_class_prefix</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.signature_expression_maxlength"><code>signature_expression_maxlength</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.render_toc"><code>render_toc</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.render_toc_title"><code>render_toc_title</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRendererConfig.toc_maxdepth"><code>toc_maxdepth</code></h3>


<h2 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer"><code>MarkdownRenderer</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer.render"><code>MarkdownRenderer.render(self, config, graph)</code></h3>


<h1 id="pydoc_markdown.contrib.renderers.mkdocs"><code>pydoc_markdown.contrib.renderers.mkdocs</code></h1>

Produces MkDocs structure.

<h2 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRendererConfig"><code>MkDocsRendererConfig</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRendererConfig.output_directory"><code>output_directory</code></h3>


<h2 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer"><code>MkDocsRenderer</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>


<h3 id="pydoc_markdown.contrib.renderers.mkdocs.MkDocsRenderer.render"><code>MkDocsRenderer.render(self, modules)</code></h3>


<h1 id="pydoc_markdown.contrib.processors"><code>pydoc_markdown.contrib.processors</code></h1>


<h1 id="pydoc_markdown.contrib.processors.sphinx"><code>pydoc_markdown.contrib.processors.sphinx</code></h1>

Provides the `SphinxProcessor` that converts reST/Sphinx syntax to
markdown compatible syntax.

<h2 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessorConfig"><code>SphinxProcessorConfig</code> Objects</h2>


<h2 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessor"><code>SphinxProcessor</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessor.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>


<h3 id="pydoc_markdown.contrib.processors.sphinx.SphinxProcessor.preprocess"><code>SphinxProcessor.preprocess(self, root, node)</code></h3>


<h1 id="pydoc_markdown.contrib.processors.pydocmd"><code>pydoc_markdown.contrib.processors.pydocmd</code></h1>

Provides the `PydocmdProcessor` class which converts the Pydoc-Markdown
highlighting syntax into Markdown.

<h2 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessorConfig"><code>PydocmdProcessorConfig</code> Objects</h2>


<h2 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor"><code>PydocmdProcessor</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>


<h3 id="pydoc_markdown.contrib.processors.pydocmd.PydocmdProcessor.process"><code>PydocmdProcessor.process(self, config, graph)</code></h3>


<h1 id="pydoc_markdown.contrib.processors.filter"><code>pydoc_markdown.contrib.processors.filter</code></h1>

Provides a processor that implements various filter capabilities.

<h2 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration"><code>FilterProcessorConfiguration</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.expression"><code>expression</code></h3>


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.documented_only"><code>documented_only</code></h3>


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.exclude_private"><code>exclude_private</code></h3>


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessorConfiguration.exclude_special"><code>exclude_special</code></h3>


<h2 id="pydoc_markdown.contrib.processors.filter.FilterProcessor"><code>FilterProcessor</code> Objects</h2>

The `filter` processor removes module and class members based on certain
criteria.

__Example__


```py
- type: filter
  expression: not name.startswith('_') and default()
```

<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessor.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>


<h3 id="pydoc_markdown.contrib.processors.filter.FilterProcessor.process"><code>FilterProcessor.process(self, config, graph)</code></h3>


<h1 id="pydoc_markdown.contrib.loaders"><code>pydoc_markdown.contrib.loaders</code></h1>


<h1 id="pydoc_markdown.contrib.loaders.python"><code>pydoc_markdown.contrib.loaders.python</code></h1>

Loads Python source code into the Pydoc-markdown reflection format.

<h2 id="pydoc_markdown.contrib.loaders.python.dedent_docstring"><code>dedent_docstring(s)</code></h2>


<h2 id="pydoc_markdown.contrib.loaders.python.find"><code>find(predicate, iterable)</code></h2>


<h2 id="pydoc_markdown.contrib.loaders.python.parse_to_ast"><code>parse_to_ast(code, filename)</code></h2>

Parses the string *code* to an AST with `lib2to3`.

<h2 id="pydoc_markdown.contrib.loaders.python.parse_file"><code>parse_file(code, filename, module_name=None)</code></h2>

Creates a reflection of the Python source in the string *code*.

<h2 id="pydoc_markdown.contrib.loaders.python.Parser"><code>Parser</code> Objects</h2>

A helper class that parses a Python AST to turn it into objects of the
[[pydoc_markdown.reflection]] module. Extracts docstrings from functions
and single-line comments.

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse"><code>Parser.parse(self, ast, filename, module_name=None)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_declaration"><code>Parser.parse_declaration(self, parent, node, decorators=None)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_statement"><code>Parser.parse_statement(self, parent, stmt)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_decorator"><code>Parser.parse_decorator(self, node)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_funcdef"><code>Parser.parse_funcdef(self, parent, node, is_async, decorators)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_parameters"><code>Parser.parse_parameters(self, parameters)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.parse_classdef"><code>Parser.parse_classdef(self, parent, node, decorators)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.location_from"><code>Parser.location_from(self, node)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_return_annotation"><code>Parser.get_return_annotation(self, node)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_most_recent_prefix"><code>Parser.get_most_recent_prefix(self, node)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_docstring_from_first_node"><code>Parser.get_docstring_from_first_node(self, parent, module_level=False)</code></h3>

This method retrieves the docstring for the block node *parent*. The
node either declares a class or function.

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_statement_docstring"><code>Parser.get_statement_docstring(self, node)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.Parser.get_hashtag_docstring_from_prefix"><code>Parser.get_hashtag_docstring_from_prefix(self, node)</code></h3>

Given a node in the AST, this method retrieves the docstring from the
closest prefix of this node (ie. any block of single-line comments that
precede this node).

The function will also return the type of docstring: A docstring that
begins with `#:` is a statement docstring, otherwise it is a block
docstring (and only used for classes/methods).

return: (docstring, doc_type)

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.prepare_docstring"><code>Parser.prepare_docstring(self, s)</code></h3>

TODO @NiklasRosenstein handle u/f prefixes of string literal?

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.nodes_to_string"><code>Parser.nodes_to_string(self, nodes)</code></h3>

Converts a list of AST nodes to a string.

<h3 id="pydoc_markdown.contrib.loaders.python.Parser.name_to_string"><code>Parser.name_to_string(self, node)</code></h3>


<h2 id="pydoc_markdown.contrib.loaders.python.ListScanner"><code>ListScanner</code> Objects</h2>

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

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.__init__"><code>ListScanner.__init__(self, lst, index=0)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.__bool__"><code>ListScanner.__bool__(self)</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.__nonzero__"><code>__nonzero__</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.current"><code>ListScanner.current(self)</code></h3>

Returns the current list element.

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.can_advance"><code>ListScanner.can_advance(self)</code></h3>

Returns `True` if there is a next element in the list.

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.advance"><code>ListScanner.advance(self, expect=False)</code></h3>

Advances the scanner to the next element in the list. If *expect* is set
to `True`, an [[IndexError]] will be raised when there is no next element.
Otherwise, `None` will be returned.

<h3 id="pydoc_markdown.contrib.loaders.python.ListScanner.safe_iter"><code>ListScanner.safe_iter(self, auto_advance=True)</code></h3>

A useful generator function that iterates over every element in the list.
You may call [[advance()]] during the iteration to retrieve the next
element in the list within a single iteration.

If *auto_advance* is `True` (default), the function generator will
always advance to the next element automatically. If it is set to `False`,
[[advance()]] must be called manually in every iteration to ensure that
the scanner has advanced at least to the next element, or a
[[RuntimeError]] will be raised.

<h2 id="pydoc_markdown.contrib.loaders.python.PythonLoaderConfig"><code>PythonLoaderConfig</code> Objects</h2>


<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoaderConfig.modules"><code>modules</code></h3>

A list of module or package names that this loader will search for and
then parse. The modules are searched using the [[sys.path]] of the current
Python interpreter, unless the [[search_path]] option is specified.

<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoaderConfig.search_path"><code>search_path</code></h3>

The module search path. If not specified, the current [[sys.path]] is
used instead. If any of the elements contain a `*` (star) symbol, it
will be expanded with [[sys.path]].

<h2 id="pydoc_markdown.contrib.loaders.python.PythonLoader"><code>PythonLoader</code> Objects</h2>

This implementation of the [[Loader]] interface parses Python modules and
packages. Which files are parsed depends on the configuration (see
[[PythonLoaderConfig]]).

<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoader.CONFIG_CLASS"><code>CONFIG_CLASS</code></h3>


<h3 id="pydoc_markdown.contrib.loaders.python.PythonLoader.load"><code>PythonLoader.load(self, config, graph)</code></h3>


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

<h2 id="pydoc_markdown.utils.import_object"><code>import_object(name)</code></h2>


<h2 id="pydoc_markdown.utils.load_entry_point"><code>load_entry_point(group, name)</code></h2>

Returns the first entry point registered to the specified *group* that
matches the *name*. If multiple entry points are registered to that name,
an `EnvironmentError` is raised.

If no entry point with the specified *name* can be found, a `ValueError`
is raised instead.

<h1 id="pydoc_markdown.main"><code>pydoc_markdown.main</code></h1>

Implements the pydoc-markdown CLI.

<h2 id="pydoc_markdown.main.PydocMarkdownConfig"><code>PydocMarkdownConfig</code> Objects</h2>


<h3 id="pydoc_markdown.main.PydocMarkdownConfig.loaders"><code>loaders</code></h3>


<h3 id="pydoc_markdown.main.PydocMarkdownConfig.processors"><code>processors</code></h3>


<h3 id="pydoc_markdown.main.PydocMarkdownConfig.renderer"><code>renderer</code></h3>


<h2 id="pydoc_markdown.main.PydocMarkdown"><code>PydocMarkdown</code> Objects</h2>

This class wraps all the functionality provided by the command-line.

<h3 id="pydoc_markdown.main.PydocMarkdown.__init__"><code>PydocMarkdown.__init__(self)</code></h3>


<h3 id="pydoc_markdown.main.PydocMarkdown.load_config"><code>PydocMarkdown.load_config(self, data)</code></h3>

Loads the configuration. *data* be a string pointing to a YAML file or
a dictionary.

<h3 id="pydoc_markdown.main.PydocMarkdown.load_module_graph"><code>PydocMarkdown.load_module_graph(self)</code></h3>


<h3 id="pydoc_markdown.main.PydocMarkdown.process"><code>PydocMarkdown.process(self)</code></h3>


<h3 id="pydoc_markdown.main.PydocMarkdown.render"><code>PydocMarkdown.render(self)</code></h3>


<h2 id="pydoc_markdown.main.main"><code>main(argv=None, prog=None)</code></h2>


