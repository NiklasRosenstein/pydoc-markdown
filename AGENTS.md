# AGENTS.md

This file applies to the entire repository.

## Project overview

Pydoc-Markdown is a Python 3.10+ CLI and library that parses Python source with
`docspec` and renders API documentation. The package uses a plugin architecture
for loaders, processors, renderers, and source linkers.

Important locations:

- `src/pydoc_markdown/`: package source.
- `src/pydoc_markdown/interfaces.py`: public plugin interfaces.
- `src/pydoc_markdown/contrib/`: built-in plugin implementations.
- `src/pydoc_markdown/main.py`: CLI and configuration handling.
- `test/`: pytest suite.
- `test/testcases/`: input/output fixtures used by renderer tests.
- `docs/`: Novella/MkDocs documentation source.
- `examples/`: example integrations; do not treat them as the primary package.
- `pyproject.toml`: authoritative dependency, entry-point, and tool configuration.

## Working guidelines

- Keep changes narrowly scoped and preserve existing public behavior unless the
  task explicitly requires a compatibility break.
- Inspect the relevant interface and nearby implementation before changing a
  plugin. When adding a built-in plugin, keep the Poetry entry-point tables in
  `pyproject.toml` in sync.
- Maintain Python 3.10 compatibility. Avoid syntax introduced in later Python
  versions unless the compatibility floor is intentionally raised.
- Follow the existing typing style, including `typing` imported as `t` where
  surrounding code does so.
- Let Ruff determine Python formatting and import ordering. The configured line
  length is 120 characters. Avoid unrelated formatting churn.
- Do not edit generated output such as `htmlcov/`, `docs/_site/`, build
  directories, or caches.
- Update user-facing documentation when behavior, configuration, CLI flags, or
  plugin contracts change.

## Tests

Add or update tests for behavior changes and bug fixes. Prefer a focused
regression test that fails without the change.

- Unit and integration tests live under `test/`; utility tests also exist next
  to their source as `*_test.py` under `src/`.
- Renderer fixtures in `test/testcases/` contain configuration, Python input,
  and expected output separated by a line of at least four hyphens. Preserve
  that format when adding cases.
- Use existing helpers in `test/utils.py` for fixture-based comparisons.

Run the narrowest relevant test while iterating, for example:

```sh
pytest test/renderers/test_markdown.py -vv
```

Before handing off a code change, run the canonical project checks:

```sh
slap test
```

The configured suite runs pytest with coverage, mypy, Ruff lint checks, and Ruff
format checks. If a full run is not possible, run the relevant pytest target
plus the affected static checks and report what was not run.

Useful project commands:

```sh
slap install --no-venv-check
slap run fmt
slap run docs:build
ruff check src test
ruff format --check src test
```

Documentation builds require the docs extras, matching CI:

```sh
slap install --extras docs --no-venv-check
```

## Changelog

Non-trivial changes should include a Slam changelog entry. Create one with:

```sh
slap changelog add -t <type> -d <description>
```

Use a concise user-facing description and an appropriate existing type. Do not
manually add a pull-request URL; CI fills it in after the pull request exists.
Trivial changes may omit an entry when they would use the repository's
`no changelog` exception.

## Final verification

Before completing work:

1. Review the diff for accidental or generated-file changes.
2. Confirm new code remains compatible with Python 3.10.
3. Run focused tests and, when practical, `slap test`.
4. Ensure documentation and changelog coverage match the user-visible impact.
