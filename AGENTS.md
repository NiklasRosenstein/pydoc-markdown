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
- `uv.lock`: locked development dependencies; update it with `uv lock` when dependencies change.
- `mise.toml`: pinned toolchain (uv, towncrier) and project tasks.
- `CHANGELOG.md` and `changelog.d/`: compiled changelog and unreleased towncrier fragments.

## Working guidelines

- Keep changes narrowly scoped and preserve existing public behavior unless the
  task explicitly requires a compatibility break.
- Inspect the relevant interface and nearby implementation before changing a
  plugin. When adding a built-in plugin, keep the `[project.entry-points]` tables
  in `pyproject.toml` in sync.
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
mise run test
```

The configured suite runs pytest with coverage, mypy, Ruff lint checks, and Ruff
format checks. If a full run is not possible, run the relevant pytest target
plus the affected static checks and report what was not run.

Useful project commands:

```sh
mise run install       # uv sync
mise run fmt
mise run docs:build
uv run ruff check src test
uv run ruff format --check src test
```

If mise is unavailable, run the commands from the task definitions in `mise.toml`
directly with `uv run`. Documentation builds use the `docs` dependency group in a
separate `.venv-docs` environment because it conflicts with the `dev` group;
`mise run docs:build` takes care of that.

## Changelog

Non-trivial changes should include a towncrier changelog fragment in
`changelog.d/`. Create one with:

```sh
mise run changelog:add <pr-number>.<type>.md --content "<description> (@author)"
```

Types are `breaking`, `feature`, `improvement`, `fix`, `docs`, `tests`, and
`hygiene`. Use a concise user-facing description. If the pull request number is
not known yet, name the fragment `+<slug>.<type>.md` and rename it once the pull
request exists; the pull-request link is generated from the file name.
Trivial changes may omit an entry when they would use the repository's
`no changelog` exception.

## Final verification

Before completing work:

1. Review the diff for accidental or generated-file changes.
2. Confirm new code remains compatible with Python 3.10.
3. Run focused tests and, when practical, `mise run test`.
4. Ensure documentation and changelog coverage match the user-visible impact.
