## Pydoc-Markdown

Generate markdown API documentation from Python code.

### How it works.

1. Your code is parsed by Pydoc-Markdown using `lib2to3` to generate an
    intermediate representation of all the information necessary to
    generate documentation files.
2. One of Pydoc-Markdown's renderers will then convert the intermediate
    representation to markdown files (or to a single file).
3. (Optional) The generated markdown can then be converted to HTML with MkDocs.

### Synopsis.

    usage: pydoc-markdown command [args ...]

    available commands:
        parse   Parse Python code and generate a .pdmir file.
        render  Render a .pdmir file to markdown.
