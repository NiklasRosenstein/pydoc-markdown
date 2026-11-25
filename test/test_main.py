from pathlib import Path

import pytest
import tomli
from click.testing import CliRunner

from pydoc_markdown import PydocMarkdown, static
from pydoc_markdown.main import RenderSession, cli

POETRY_PYPROJECT = '[tool.poetry]\nname = "example"\n'
CONFIGURED_PYPROJECT = '[tool.pydoc-markdown.renderer]\ntype = "markdown"\n'


@pytest.fixture(autouse=True)
def _cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


def test_bootstrap_creates_yaml_next_to_poetry_pyproject() -> None:
    Path("pyproject.toml").write_text(POETRY_PYPROJECT)

    result = CliRunner().invoke(cli, ["--bootstrap", "mkdocs"])

    assert result.exit_code == 0, result.output
    assert result.output == "created pydoc-markdown.yaml\n"
    assert Path("pydoc-markdown.yaml").read_text() == static.DEFAULT_MKDOCS_CONFIG
    assert Path("pyproject.toml").read_text() == POETRY_PYPROJECT


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        pytest.param("pyproject.toml", CONFIGURED_PYPROJECT, id="configured-pyproject"),
        pytest.param("pydoc-markdown.yaml", "renderer:\n  type: markdown\n", id="yaml"),
        pytest.param("pydoc-markdown.yml", "renderer:\n  type: markdown\n", id="yml"),
    ],
)
def test_bootstrap_refuses_to_shadow_existing_config(filename: str, content: str) -> None:
    Path(filename).write_text(content)

    result = CliRunner().invoke(cli, ["--bootstrap", "mkdocs"])

    assert result.exit_code == 1
    assert result.output == f"error: file already exists: '{filename}'\n"
    assert [path.name for path in Path().iterdir()] == [filename]
    assert Path(filename).read_text() == content


@pytest.mark.parametrize(
    ("files", "ignored"),
    [
        pytest.param({"pyproject.toml": POETRY_PYPROJECT}, None, id="unconfigured-pyproject"),
        pytest.param({"pyproject.toml": CONFIGURED_PYPROJECT}, "pyproject.toml", id="configured-pyproject"),
        pytest.param(
            {"pyproject.toml": CONFIGURED_PYPROJECT, "pydoc-markdown.yml": "{}\n"},
            "pydoc-markdown.yml",
            id="yaml-takes-precedence",
        ),
    ],
)
def test_quick_cli_options_warn_only_when_ignoring_a_config(
    monkeypatch: pytest.MonkeyPatch, files: dict, ignored: str | None
) -> None:
    loaded_config: list = []

    def load(session: RenderSession) -> PydocMarkdown:
        loaded_config.append(session.config)
        return PydocMarkdown()

    monkeypatch.setattr(RenderSession, "load", load)
    monkeypatch.setattr(RenderSession, "render", lambda *_: [])
    for filename, content in files.items():
        Path(filename).write_text(content)

    result = CliRunner().invoke(cli, ["--module", "example"])

    assert result.exit_code == 0, result.output
    assert loaded_config == [None]
    if ignored is None:
        assert result.output == ""
    else:
        assert result.output == (
            "warning: quick CLI options disable implicit configuration loading; "
            f"ignoring '{ignored}'. Pass the configuration filename explicitly "
            "to apply CLI overrides to it.\n"
        )


def test_malformed_pyproject_reports_parse_error() -> None:
    Path("pyproject.toml").write_text("[tool.pydoc-markdown\n")

    result = CliRunner().invoke(cli, [])

    assert result.exit_code != 0
    assert "config file not found" not in result.output
    assert isinstance(result.exception, tomli.TOMLDecodeError)


def test_py2_flag_is_deprecated_and_keeps_implicit_config() -> None:
    Path("pydoc-markdown.yml").write_text("renderer:\n  type: markdown\n  filename: out.md\n")

    result = CliRunner().invoke(cli, ["--py3"])

    assert result.exit_code == 0, result.output
    assert "--py2/--py3 is deprecated and has no effect" in result.output
    assert Path("out.md").exists()


def test_build_rejects_renderer_without_builder_support() -> None:
    Path("pydoc-markdown.yml").write_text("renderer:\n  type: markdown\n")

    result = CliRunner().invoke(cli, ["--build"])

    assert result.exit_code == 1
    assert result.output == "error: renderer 'MarkdownRenderer' cannot be used with --build\n"


def test_bootstrap_readthedocs_refuses_to_replace_legacy_config_name() -> None:
    Path(".readthedocs.yml").write_text("version: 2\n")

    result = CliRunner().invoke(cli, ["--bootstrap", "readthedocs"])

    assert result.exit_code == 1
    assert result.output == "error: file already exists: '.readthedocs.yml'\n"
    assert not Path(".readthedocs.yaml").exists()
