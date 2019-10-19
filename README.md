# pydoc-markdown

<table><tr><td>master</td><td>

[![CircleCI](https://circleci.com/gh/NiklasRosenstein/pydoc-markdown/tree/master.svg?style=svg)](https://circleci.com/gh/NiklasRosenstein/pydoc-markdown/tree/master)
</td><td>develop</td><td>

[![CircleCI](https://circleci.com/gh/NiklasRosenstein/pydoc-markdown/tree/develop.svg?style=svg)](https://circleci.com/gh/NiklasRosenstein/pydoc-markdown/tree/develop)    
</td></tr></table>

Pydoc-markdown produces Markdown API documentation from Python code.

__Table of Contents__

* [Get started](#get-started)
* [Syntax](#syntax)
* [State of Pydoc-markdown 3.x](#state-of-pydoc-markdown-3x)
* [Migrating from Pydoc-markdown 2.x](#migrating-from-pydoc-markdown-2x)

## Get started

Install Pydoc-markdown from GitHub:

```
$ pip install git+https://github.com/NiklasRosenstein/pydoc-markdown.git@develop
```

Simple mode:

    $ pydoc-markdown --modules mymodule --search-path src/ > out.md

Project mode:

    $ cat pydoc-markdown.yml
    loaders:
      - type: python
        modules: [mymodule]
        search_path: [src]
    processors:
      - type: pydocmd
      - type: filter
        document_only: true
    renderer:
      type: markdown
    $ pydoc-markdown > out.md

## Syntax

Just use Markdown syntax in your docstrings. There are some special treatments
applied by the `pydocmd` processor though.

* `[[my_function()]]` is a reference to a function (resolved in the current
  static scope of the docstring), for members in the current scope you would
  prefix it with a hash (eg. `[[#my_method()]]`)
* `# Section Name` in a docstring will be converted to just bold text

## State of Pydoc-markdown 3.x

* [x] Parsing with `lib2to3`
* [x] CLI with a "simple" mode
* [ ] Render Markdown files for MkDocs (`pydoc_markdown.contribs.renderers.mkdocs`)
* [ ] Port community contributions of 2.x to 3.x
* [ ] Add backwards-compatible processor for links (translating `#my_function()`
      to `[[my_function()]]`)
* [ ] Understand hints in Python docs (g. `# doc: ignore`)
* [ ] Capture `TODO` and `NOTE` comments in classes and functions and optionally
      include that information in generated docs
* [ ] Parse and resolve links to other objects in the document

## Migrating from Pydoc-markdown 2.x

Pydoc-markdown 3 is a major rewrite and comes with a great deal of
architectural changes. First and foremost, it no longer executes Python code
to retrieve docstrings. Instead, it uses the `lib2to3` module to parse the
code and convert it into a "reflection" of the code.

Using `lib2to3` to parse the code has three main advantages:

1. No longer need to execute Python code
2. Python version used to generated docs can (usually) differ from the Python
   version that the code was written for
3. Adds the ability to extract docstrings from single-line comments

However it also means that Pydoc-markdown inherits the quirks of `lib2to3`.
One of these quirks is for example (state CPython 3.7) that a function
argument in Python 3 may be called "print", but `lib2to3` treats this as a
syntax error.

Pydoc-markdown 3.x also uses a different syntax for links to other objects,
but a backwards-compatible processor will be added.
