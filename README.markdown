__NAME__

<a href="https://gitter.im/NiklasRosenstein/pydoc-markdown">
  <img src="https://badges.gitter.im/Join%20Chat.svg"></img>
</a>

[`pydoc_markdown`](https://pypi.python.org/pypi/pydoc-markdown) - simple generator for Markdown formatted Python docs

__SYNOPSIS__

    pydoc-markdown [-h] module

__DESCRIPTION__

Simple (ie. quick and dirty) script to generate a Markdown
formatted help on a Python module. Contributions are welcome.

Project Homepage:  https://github.com/NiklasRosenstein/pydoc-markdown

```
positional arguments:
  module      name of the module to generate docs for

optional arguments:
  -h, --help  show this help message and exit
```

__INSTALLATION__

    $ pip install pydoc-markdown

or for the latest development version

    $ git clone https://github.com/NiklasRosenstein/pydoc-markdown
    $ cd pydoc-markdown
    $ pip install -e .

__EXAMPLES__

    $ pydoc-markdown glob

    # glob Module
    > Filename globbing utility.



    ## Data
    - `magic_check = re.compile('([*?[])')`
    - `magic_check_bytes = re.compile(b'([*?[])')`

    ## Functions

    ##### `escape(pathname)`

    > Escape all special characters.



    ##### `glob(pathname)`

    > Return a list of paths matching a pathname pattern.
    >
    >     The pattern may contain simple shell-style wildcards a la
    >     fnmatch. However, unlike fnmatch, filenames starting with a
    >     dot are special cases that are not matched by '*' and '?'
    >     patterns.



    ##### `glob0(dirname, basename)`



    ##### `glob1(dirname, pattern)`



    ##### `has_magic(s)`



    ##### `iglob(pathname)`

    > Return an iterator which yields the paths matching a pathname pattern.
    >
    >     The pattern may contain simple shell-style wildcards a la
    >     fnmatch. However, unlike fnmatch, filenames starting with a
    >     dot are special cases that are not matched by '*' and '?'
    >     patterns.
