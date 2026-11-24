# Contributing to Pydoc-Markdown

  [0]: https://github.com/NiklasRosenstein/pydoc-markdown/discussions
  [mise]: https://mise.jdx.dev/
  [uv]: https://docs.astral.sh/uv/
  [towncrier]: https://towncrier.readthedocs.io/

Contributions to Pydoc-Markdown are very welcome!

If you want to talk about a potential contribution before investing any time, please do create a new topic on
[GitHub Discussions][0].

## Pull request requirements

* Please look to adhere to the existing code style (2-space indendation, 120 character line length limit)
* Pull requests should contain at least one new changelog entry unless the change is trivial (see below for details)

## Development setup

Pydoc-Markdown uses [uv][] to manage Python, the virtual environment and the lock file, and [mise][] to install the
toolchain and run project tasks. After installing mise, run the following from the repository root:

    $ mise install          # installs uv and towncrier at the versions pinned in mise.toml
    $ mise run install      # creates .venv with the development dependencies (uv sync)
    $ mise run test         # runs pytest, mypy, Ruff lint and Ruff format checks
    $ mise run fmt          # applies Ruff fixes and formatting
    $ mise run docs:dev     # serves the documentation with live reload

Use `mise tasks` to list all available tasks. Without mise, the equivalent uv commands work just as well, e.g.
`uv run pytest` or `uv run mypy src/`.

## Changelog entries

Pydoc-Markdown uses [towncrier][] to manage the changelog. Each pull request adds one or more fragments to the
`changelog.d/` directory, named `<pr-number>.<type>.md`, where `<type>` is one of `breaking`, `feature`,
`improvement`, `fix`, `docs`, `tests` or `hygiene`. The file contains a short, user-facing description that ends with
your GitHub handle, for example:

    $ mise run changelog:add 123.fix.md --content "Fix rendering of nested classes. (@your-handle)"

If you don't know the pull request number yet, name the fragment `+<some-slug>.<type>.md` and rename it once the pull
request exists. A link to the pull request is added automatically when the changelog is compiled. Preview the result
with `mise run changelog:preview`.

Trivial changes may skip the changelog by adding the `no changelog` label to the pull request. Dependency update pull
requests opened by Renovate skip the check automatically.

## Releasing

Maintainers create a release from an up-to-date `develop` branch with:

    $ mise run release <major|minor|patch>

This bumps the version in `pyproject.toml` and `src/pydoc_markdown/__init__.py`, compiles the fragments into
`CHANGELOG.md`, and creates a release commit plus a `v<version>` tag that you can then push.
