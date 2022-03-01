# Read the Docs

  [readthedocs-custom-steps]: https://pypi.org/project/readthedocs-custom-steps/

Using Pydoc-Markdown on [readthedocs.org](https://readthedocs.org/) requires some "hacking" because natively it
does not allow you to run any custom commands. Using [readthedocs-custom-steps][], you can hook into the call
that RTD expects to generate the documentation using Sphinx/MkDocs and run your own commands instead.

__Example__

=== ".readthedocs.yml"

    ```yaml
    version: 2
    mkdocs: {}  # tell readthedocs to use mkdocs
    python:
      version: 3.7
      install:
      - method: pip
        extra_requirements:
        - rtd
    ```

=== "setup.cfg"

    ```ini
    [options.extras_require]
    rtd = readthedocs-custom-steps==0.6.2
    ```

=== "pyproject.toml"

    ```toml
    # ...

    [tool.readthedocs-custom-steps]
    script = """
    novella --site-dir _site/html
    """
    ```
