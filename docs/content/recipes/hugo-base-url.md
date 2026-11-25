# Hugo `baseURL` per version

Hugo needs `baseURL` to generate permalinks. If you publish several versions of your docs (for example on Read the
Docs), each one needs a different `baseURL`. Use [configuration templating](../guides/configuration.md#templating) to
compute it from the environment:

```yaml title="pydoc-markdown.yaml"
#@ def base_url():
#@    if env.READTHEDOCS:
#@      return "https://my-project.readthedocs.io/en/" + env.READTHEDOCS_VERSION + "/"
#@    else:
#@      return None
#@ end

renderer:
  type: hugo
  config:
    baseURL: #@ base_url()
```
