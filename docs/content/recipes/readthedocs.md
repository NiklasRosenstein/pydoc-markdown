# Read the Docs

[Read the Docs](https://readthedocs.org/) lets you replace its build with your own commands via
[`build.commands`](https://docs.readthedocs.io/en/stable/build-customization.html#override-the-build-process). Write
the built HTML to `$READTHEDOCS_OUTPUT/html`.

=== "Configuration file (MkDocs renderer)"

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

=== "Novella"

    ```yaml title=".readthedocs.yaml"
    version: 2
    build:
      os: ubuntu-24.04
      tools:
        python: "3.12"
      commands:
        - pip install novella pydoc-markdown mkdocs mkdocs-material
        - cd docs && novella --site-dir "$READTHEDOCS_OUTPUT/html"
    ```

Versioned builds can use the `READTHEDOCS_VERSION` environment variable, for example to set the
[Hugo `baseURL`](hugo-base-url.md).

!!! note

    `pydoc-markdown --bootstrap readthedocs` still generates an older setup based on
    [readthedocs-custom-steps](https://pypi.org/project/readthedocs-custom-steps/) and the removed `python.version`
    Read the Docs setting. Prefer the configuration above; see [Deprecations](../deprecations.md).
