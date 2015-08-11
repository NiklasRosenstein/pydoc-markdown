
# pydoc_markdown Module
> Simple script to get a Markdown formatted documentation for a Python
> module or package.



## Data
- `Py3 = True` 
- `class_types = (<class 'type'>,)` 
- `function_types = (<class 'function'>,...` 
- `method_types = (<class 'method'>, <...` 
- `special_member_types = (<class 'property'>,...` 
- `special_names = frozenset({'__weakre...` 
- `string_types = (<class 'str'>,)` 

## Functions

##### `argspec_format(func)` 

> Uses the :mod:`inspect` module to generate the argument specs of
> the specified function and returns it including parantheses.
> 
> Args:
>     func (function): The function to get the argument specs for.
> Raises:
>     TypeError: If *func* is not a function.



##### `import_module(module_name)` 

> Imports the specified module by name.



##### `main()` 



##### `write_class(md, cls, name=None)` 



##### `write_class_member(md, value, name)` 



##### `write_docstring(md, doc)` 

> Writes the specified Python *docstring* to the markdown writer.



##### `write_function(md, func, name, prefix=None)` 



##### `write_member(md, member, prefix=None)` 



##### `write_module(md, module, recursive=True)` 

> Formats the specified Python module and its contents into markdown
> syntax using the :class:`MarkdownWriter` *md*. If *recursive* is
> specified, all sub-packages and -modules will be included.



## pydoc_markdown.MarkdownWriter Objects



##### `__init__(self, fp)` 



##### `blockquote(self, text)` 



##### `code(self, text, italic=False, bold=False)` 

> Encloses *text* in backticks.



##### `code_block(self, code, language=None)` 

> Writes *code* as a code-block to the code. If *language* is
> not specified, the code will be written as an indented code
> block, otherwise the triple code block formatting is used.
> You should make sure the code block is preceeded by a newline.



##### `header(self, text=None)` 

> Begins a markdown header with the appropriate depth. Use
> :meth:`push_header` and :meth:`pop_header` to change the
> header indentation level.



##### `link(self, text, alias=None, url=None)` 

> Writes a link into the markdown file. If only *text* is
> specified, the alias will be the *text* itself. If an *url*
> is passed, an inline link will be generated. Conflicts with
> providing the *alias* option.



##### `newline(self)` 

> Writes a newline to the file.



##### `pop_header(self)` 



##### `push_header(self, level_increase=1)` 



##### `text(self, text)` 

> Writes *text* to the file.



##### `ul_item(self)` 


