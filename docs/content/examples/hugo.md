# Hugo

## Tips & Tricks

### Hugo `baseURL`

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
