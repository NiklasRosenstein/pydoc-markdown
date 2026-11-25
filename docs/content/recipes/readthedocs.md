# Read the Docs

[Read the Docs](https://readthedocs.org/) lets you replace its build with your own commands via
[`build.commands`](https://docs.readthedocs.io/en/stable/build-customization.html#override-the-build-process). Write
the built HTML to `$READTHEDOCS_OUTPUT/html`.

Combine it with a configuration that uses the [`mkdocs` renderer](../guides/static-site-generators.md#mkdocs):

```yaml title=".readthedocs.yaml"
version: 2
build:
  os: ubuntu-24.04
  tools:
    python: "3.12"
  commands:
    - pip install pydoc-markdown mkdocs
    - pydoc-markdown --build --site-dir "$READTHEDOCS_OUTPUT/html"
```

`pydoc-markdown --bootstrap readthedocs` writes this file for you.

Versioned builds can use the `READTHEDOCS_VERSION` environment variable, for example to set the
[Hugo `baseURL`](hugo-base-url.md).
