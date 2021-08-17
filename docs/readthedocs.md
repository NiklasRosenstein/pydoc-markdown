# Read the Docs

  [readthedocs-custom-steps]: https://pypi.org/project/readthedocs-custom-steps/

Projects that use Pydoc-Markdown can be built on __Read the Docs__ by using the
[readthedocs-custom-steps][] package. A couple of files are needed to make this work.

__.readthedocs.yml__

```yml
version: 2
mkdocs: {}  # tell readthedocs to use mkdocs
python:
  version: 3.7
  install:
  - method: pip
  - requirements: docs/.readthedocs-requirements.txt
```

__docs/.readthedocs-requirements.txt__

```
readthedocs-custom-steps==0.5.1
```

__docs/.readthedocs-custom-steps.yml__

```yml
steps:
- pydoc-markdown --build --site-dir $SITE_DIR
```

You can use the `pydoc-markdown --bootstrap readthedocs` command as a shortcut to create
these files.

### Hugo baseURL

When using Hugo, usually you want to set the `baseURL` configuration so that it can generated
permalinks properly. If you are building on Read the Docs, chances are that you will have
multiple versions of the documentation, which all require a different `baseURL`.

Pydoc-Markdown configuration files are pre-processed with a [YTT][]-like templating language.

  [YTT]: https://get-ytt.io/

```yml
#@ def base_url():
#@    if env.READTHEDOCS:
#@      return "https://pydoc-markdown.readthedocs.io/en/" + env.READTHEDOCS_VERSION + "/"
#@    else:
#@      return None
#@ end

renderer:
  type: hugo
  config:
    baseURL: #@ base_url()
```
