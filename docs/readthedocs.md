# Read the Docs

  [readthedocs-custom-steps]: https://pypi.org/project/readthedocs-custom-steps/

Projects that use Pydoc-Markdown can be built on __Read the Docs__ by using the
[readthedocs-custom-steps][] package. A couple of files are needed to make this work.

__.readthedocs-requirements.txt__

```
readthedocs-custom-steps
```

__.readthedocs.yml__

```yml
version: 2
mkdocs: {}  # tell readthedocs to use mkdocs
python:
  version: 3.7
  install:
  - method: pip
    path: pydoc-markdown  # replace with the path to your package
  - requirements: .readthedocs-requirements.txt
```

__.readthedocs-custom-steps.yml__

```yml
steps:
- pydoc-markdown --build --site-dir $SITE_DIR
```

You can use the `pydoc-markdown --bootstrap readthedocs` command as a shortcut to create
these files.
