# pydoc-markdown-mkdocs-proxy

> __Important__: This module should not be installed outside of a ReadTheDocs build environment.

Installs a bash script in place of the current Python executable that routes an invokation of
`python -m mkdocs build` to Pydoc-Markdown instead. This allows you to build documentation using
Pydoc-Markdown on [readthedocs.org](https://readthedocs.org).

Example `.readthedocs.yml`:

```yml
version: 2
mkdocs: {}  # Tell RTD to use MkDocs.
python:
  version: 3.7
  install:
    - method: pip
      path: .
    - method: pip
      path: pydoc-markdown-readthedocs-mkdocs-proxy
```

---

<p align="center">Copyright &copy; 2020 Niklas Rosenstein</p>
