# Pydoc-Markdown Roadmap

Last updated: 2026-08-01

This roadmap turns the open GitHub issue inventory into an ordered maintenance
plan. GitHub issues remain the source for user reports and discussion; this file
is the source for sequencing, scope, and completion criteria.

## Principles

- Restore and preserve a green build before merging feature work.
- Prioritize core loading, processing, and Markdown correctness over new
  site-generator integrations.
- Treat YAML configuration and its page model as supported functionality. It
  was explicitly un-deprecated in v4.7 after community feedback.
- Preserve Python 3.8 compatibility unless a separate version-policy decision
  changes it.
- Close issues only with evidence and a short explanatory comment. Age alone is
  not a reason to close an issue.
- Prefer small, reviewable PRs. A bundled maintenance PR is acceptable only when
  its changes remain independent, low-risk, and covered by focused tests.
- Route parser and source-model behavior upstream when `docstring-parser` or
  `docspec-python` is the correct ownership boundary.

## Schedule

The durations are rough effort ranges for one maintainer and express ordering,
not delivery commitments.

| Order | Milestone | Scope | Expected PRs | Rough effort |
|---:|---|---|---:|---:|
| 0 | Issue hygiene | Close completed, superseded, obsolete, and verified-stale reports | 0 | 0.5–1 day |
| 1 | Compatibility baseline | Consolidate tooling on Ruff, restore CI, fix Databind constraints, verify Python 3.8–3.14 | 2 | 1–3 days |
| 2 | Small core fixes | Page title, deterministic ordering, page-source watching | 1–2 | 2–4 days |
| 3 | Packaging and CLI maintenance | Conda-forge update and Poetry-aware bootstrap | 2 repositories/PRs | 1–3 days |
| 4 | Docstring processing | Dependency upgrade, NumPy support, indentation and code-block fixes | 3–5 | 1–2 weeks |
| 5 | Core model and linking | Markdown references, exports, stubs, and type links | 3–5 plus upstream | 2–4 weeks |
| 6 | Integration policy | Decide the future of built-in MkDocs/Docusaurus renderers, then act | 1 decision plus optional fixes | 1–2 weeks |
| 7 | Release readiness | Full matrix, docs, changelog, and remaining backlog review | 1 | 1–2 days |

## Milestone 0 — Issue hygiene

No issue should be closed silently. Each closure comment should state which of
the following applies: implemented, superseded, obsolete configuration,
unsupported legacy path, dependency-resolved, or not reproducible on the
current release.

### Ready to close with existing evidence

- [x] [#134](https://github.com/NiklasRosenstein/pydoc-markdown/issues/134):
  close as implemented by the Novella `@pydoc` integration merged in PR #245.
- [x] [#170](https://github.com/NiklasRosenstein/pydoc-markdown/issues/170):
  close as fixed; commit `1084842` is on `develop` and the multiline-parameter
  regression test remains in the current suite.
- [x] [#297](https://github.com/NiklasRosenstein/pydoc-markdown/issues/297):
  close after linking PR #317 and its regression test for more than nine
  escaped code spans/blockquotes.
- [x] [#313](https://github.com/NiklasRosenstein/pydoc-markdown/issues/313):
  close as superseded by the active Renovate dashboard, #351.
- [x] [#336](https://github.com/NiklasRosenstein/pydoc-markdown/issues/336):
  close or move to Discussions because it is informational and requests no
  repository change.

### Close as intentionally superseded

- [ ] [#236](https://github.com/NiklasRosenstein/pydoc-markdown/issues/236):
  verify current Novella documentation links, then close because Novella uses
  real source pages and supersedes the broken legacy edit-link path.

### Verified and closed

- [x] Verify [#275](https://github.com/NiklasRosenstein/pydoc-markdown/issues/275).
  The exact configuration fails on 4.6.4 but passes on 4.6.3, confirming a real
  regression. PR #294 fixed the recursive page type and added configuration
  deserialization tests; the configuration passes on 4.8.2 with Python 3.8 and
  3.14.
  - [x] Closed as fixed in 4.8.1, linking PR #294. Note that Python 3.7 is no
    longer supported.
- [x] Verify [#276](https://github.com/NiklasRosenstein/pydoc-markdown/issues/276).
  Normal package loading, module loading, discovery, CLI loading, and the
  maintainer's MkDocs reproduction all render `my_package.demo` on current
  `develop`. Only explicitly loading `my_package.__init__` retains that literal
  module name.
  - [x] Closed as not reproducible with normal package loading, recommend loading
    `my_package`, and invite reopening with the original configuration.
- [x] Verify [#348](https://github.com/NiklasRosenstein/pydoc-markdown/issues/348).
  The exact Python 3.14 failure reproduces with TypeAPI 2.2.4 and passes with
  TypeAPI 2.3.0, independently of whether Databind is 4.5.2 or 4.5.5. Existing
  YAML configuration tests detect the failure and currently pass on Python
  3.14.
  - [x] Closed as dependency-resolved with `poetry update typeapi` guidance.
    A future compatibility change should guarantee `typeapi >= 2.3.0` on Python
    3.14 for old lockfiles and make Python 3.14 explicit in CI before the
    floating `3.x` entry advances.

### Keep open by design

- [ ] [#351](https://github.com/NiklasRosenstein/pydoc-markdown/issues/351): keep
  as the active Renovate dependency dashboard; do not treat it as a normal
  feature backlog item.

## Milestone 1 — Compatibility baseline

No later milestone starts until the default branch is green.

### PR 1A: Consolidate linting and formatting on Ruff

The repository currently uses Black and isort; it does not configure Flake8.
Ruff should replace Black and isort and become the project linter. Keep mypy as
the type checker. Keep YAPF as a runtime dependency because the Markdown
renderer uses it to format code in generated documentation.

- [x] Add a pinned Ruff development dependency and configure it for Python 3.8,
  a 120-character line length, formatting, import sorting, and an initial
  low-surprise lint baseline (`E4`, `E7`, `E9`, `F`, and `I`).
- [x] Replace the Black and isort `slap test` checks with `ruff format --check`
  and `ruff check`. Replace `slap run fmt` with Ruff's fix and format commands.
- [x] Remove the Black and isort dependencies and their tool configuration.
  There is no Flake8 dependency or configuration to remove.
- [x] Apply the Ruff formatting/import changes as a mechanical change, then fix
  remaining lint findings without unrelated behavioral changes.
- [x] Update `AGENTS.md` and contributor-facing command documentation only when
  the Ruff migration lands, so repository guidance continues to match the
  commands available on each branch.

Status: implemented and independently reviewed on `codex/ruff-tooling`; awaiting
PR approval and merge. Ruff lint/format checks, Python 3.8 compilation, and all
73 tests pass. The four existing mypy errors on Python 3.14 remain scoped to PR
1B.

### PR 1B: Restore the compatibility baseline

- [ ] Fix the current mypy failures in `main.py` and `util/watchdog.py`.
- [ ] Pin development tools tightly enough that CI does not change underneath
  the project without review, including the Ruff and mypy versions.
- [ ] Address [#332](https://github.com/NiklasRosenstein/pydoc-markdown/issues/332)
  by excluding broken Databind 4.5.2 and evaluating migration from the proxy
  `databind.core`/`databind.json` packages to the consolidated `databind`
  package.
- [ ] Add configuration-import smoke coverage on the oldest and newest
  supported Python versions.
- [x] Complete the #348 verification and closure from Milestone 0.

Acceptance criteria:

- `slap test` passes locally.
- `ruff check src test` and `ruff format --check src test` pass, and Black and
  isort are no longer referenced by project configuration or contributor
  guidance.
- Mypy remains enabled and passes; YAPF remains available to the Markdown
  renderer at runtime.
- CI passes on Python 3.8, 3.9, 3.10, 3.11, 3.12, and `3.x` (currently 3.14).
- A clean installation cannot resolve to Databind 4.5.2.

## Milestone 2 — Small core fixes

### PR 2A: Small Markdown output fixes

It is reasonable to combine the following issues into one PR if each change is
an independent commit and has a focused regression test:

- [ ] [#307](https://github.com/NiklasRosenstein/pydoc-markdown/issues/307):
  add a configurable `MarkdownRenderer.page_title` fallback for standalone
  rendering.
- [ ] [#340](https://github.com/NiklasRosenstein/pydoc-markdown/issues/340):
  make module/package discovery deterministic. Preserve member source order by
  default unless a separately documented sorting option is selected. Reuse the
  sound parts of PR #342, but do not inherit its default behavior change or TOC
  indentation regression.

### PR 2B: YAML page-model fixes

These belong together because both affect the supported `GenericPage` model:

- [ ] [#54](https://github.com/NiklasRosenstein/pydoc-markdown/issues/54): adapt
  the old `generate:`/`module+` request to the current supported YAML model.
  Add an `exclude` glob list to `renderer.pages[]`, applied after `contents`, so
  individual pages can include a module tree while omitting selected children.
  Keep `FilterProcessor.expression` as the global filtering mechanism.
- [ ] [#154](https://github.com/NiklasRosenstein/pydoc-markdown/issues/154):
  include configured `Page.source` files in server watch paths.

Split #154 if it requires a new public renderer interface rather than a small
page-model hook. Do not add dependency or packaging changes to either PR.

Acceptance criteria:

- Each issue has a failing-before/passing-after test.
- Sorting is deterministic without unexpectedly reordering documented members.
- Page exclusions retain required ancestor modules while removing every
  matching child.
- Server watch paths are resolved relative to the configuration context.
- Existing renderer fixtures remain unchanged unless the change is intentional.

## Milestone 3 — Packaging and CLI maintenance

### External feedstock PR

- [ ] [#329](https://github.com/NiklasRosenstein/pydoc-markdown/issues/329):
  update `conda-forge/pydoc-markdown-feedstock` from 4.5.0 to 4.8.2, update its
  dependency constraints, rerender, and verify import plus CLI smoke tests.

This cannot be part of a pydoc-markdown PR because it belongs to a different
repository.

### CLI bootstrap PR

- [ ] [#197](https://github.com/NiklasRosenstein/pydoc-markdown/issues/197):
  when `pyproject.toml` already exists, create `pydoc-markdown.yml` rather than
  failing or rewriting the existing TOML. Warn when quick CLI options suppress
  implicit configuration loading.

## Milestone 4 — Docstring processing

### PR 1: Parser dependency modernization

- [ ] Upgrade `docstring-parser` from the `^0.11` line to a current compatible
  release and document behavior changes.
- [ ] [#251](https://github.com/NiklasRosenstein/pydoc-markdown/issues/251):
  add NumPy-style fixtures and explicit/AUTO style selection, using upstream
  Numpydoc support rather than a new handwritten parser.
- [ ] [#259](https://github.com/NiklasRosenstein/pydoc-markdown/issues/259):
  retest space-indented blocks against the upgraded parser and send remaining
  parser defects upstream.

### PR 2: Google processor indentation model

- [ ] [#182](https://github.com/NiklasRosenstein/pydoc-markdown/issues/182):
  preserve literal-code indentation.
- [ ] [#296](https://github.com/NiklasRosenstein/pydoc-markdown/issues/296):
  retest after the earlier indented-fence fix and add the exact report as a
  fixture if it still fails.
- [ ] [#320](https://github.com/NiklasRosenstein/pydoc-markdown/issues/320):
  preserve nested-list indentation.

Implement these together by replacing unconditional `line.strip()` behavior
with section-aware parsing that preserves relative indentation.

### Follow-up PRs

- [ ] [#327](https://github.com/NiklasRosenstein/pydoc-markdown/issues/327):
  optionally recognize doctests inside `Examples:` sections and fence them as
  Python without rewriting arbitrary prose.
- [ ] [#299](https://github.com/NiklasRosenstein/pydoc-markdown/issues/299):
  support reST `::` literal blocks only if still missing after the parser
  upgrade.
- [ ] [#300](https://github.com/NiklasRosenstein/pydoc-markdown/issues/300):
  define a supported reST subset; route full reST conversion upstream or to an
  external converter instead of growing a second general reST parser here.

## Milestone 5 — Core model and linking

### Markdown correctness

- [ ] [#125](https://github.com/NiklasRosenstein/pydoc-markdown/issues/125):
  namespace reference-style Markdown links by API object during rendering so
  multiple docstrings cannot redefine the same label.

### Loader and source model

- [ ] [#316](https://github.com/NiklasRosenstein/pydoc-markdown/issues/316):
  shepherd `python-docspec` PR #101, then bump `docspec-python` and add `.pyi`
  discovery/loading tests.
- [ ] [#220](https://github.com/NiklasRosenstein/pydoc-markdown/issues/220):
  design static handling for literal `__all__` and imported indirections in
  `docspec-python`; do not execute documented modules.

### Type and cross-reference linking

- [ ] [#301](https://github.com/NiklasRosenstein/pydoc-markdown/issues/301) and
  [#346](https://github.com/NiklasRosenstein/pydoc-markdown/issues/346): first
  document that the current processor recognizes explicit `#Name` references,
  not arbitrary type annotations. Then design type-expression parsing and an
  indirection-aware resolver before implementing automatic links.

## Milestone 6 — Integration policy

YAML configuration and YAML-defined pages are supported. Before expanding the
built-in site-generator adapters, separately record how far MkDocs and
Docusaurus compatibility should extend:

- **Maintain:** keep MkDocs and Docusaurus renderers supported, add compatibility
  tests, and fix their open issues.
- **Compatibility only:** accept small bug fixes but direct new features to
  Novella or external plugins.
- **Deprecate:** document migration paths and close renderer-specific feature
  requests with that rationale.

### If MkDocs remains maintained

- [ ] [#94](https://github.com/NiklasRosenstein/pydoc-markdown/issues/94): copy
  and rewrite relative Markdown image assets from page sources.
- [ ] [#206](https://github.com/NiklasRosenstein/pydoc-markdown/issues/206):
  decide whether to support Read the Docs/MkDocs argument pass-through.
- [ ] [#215](https://github.com/NiklasRosenstein/pydoc-markdown/issues/215):
  resolve and copy `extra_css` and `extra_javascript` assets.

### If Docusaurus remains maintained

- [ ] [#184](https://github.com/NiklasRosenstein/pydoc-markdown/issues/184):
  add opt-in semantic-section-to-admonition rendering.
- [ ] [#309](https://github.com/NiklasRosenstein/pydoc-markdown/issues/309):
  generate a sidebar forest for multiple top-level packages.
- [ ] [#325](https://github.com/NiklasRosenstein/pydoc-markdown/issues/325):
  add context-aware MDX brace escaping outside code spans and fences.

### External integrations

- [ ] [#344](https://github.com/NiklasRosenstein/pydoc-markdown/issues/344):
  encourage the proposed Mintlify renderer as an entry-point plugin. Bring it
  into core only with tests, documentation, and an explicit maintenance owner.

## Milestone 7 — Release readiness

- [ ] Run the complete test, formatting, typing, and documentation suite.
- [ ] Verify every supported Python version in CI.
- [ ] Review all changelog entries for user-facing changes.
- [ ] Confirm every issue resolved by the release has a closure comment linking
  the implementing PR or verification evidence.
- [ ] Revisit all remaining open issues and update this roadmap where scope or
  priority changed.

## PR boundaries

The quick fixes should **not all be placed in one PR**:

- #307 and #340 may form one small Markdown-output PR.
- #54 and #154 may form a second YAML page-model PR; split #154 if it requires
  a broader public interface.
- #332 stays in the compatibility-baseline PR because dependency resolution and
  supported-version behavior require isolated review.
- #329 must be a separate PR in the conda-forge feedstock repository.
- #197 should remain separate because it changes file-creation and CLI UX.

If the small core-maintenance PR becomes difficult to describe in one sentence,
requires a public interface for #154, or makes a failure hard to attribute,
split it before review.
