import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from pydoc_markdown import PydocMarkdown, static
from pydoc_markdown.main import RenderSession, cli


def test_bootstrap_creates_yaml_without_changing_poetry_pyproject() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        pyproject = Path("pyproject.toml")
        original_pyproject = '[tool.poetry]\nname = "example"\n'
        pyproject.write_text(original_pyproject)

        result = runner.invoke(cli, ["--bootstrap", "mkdocs"])

        assert result.exit_code == 0, result.output
        assert result.output == "created pydoc-markdown.yml\n"
        assert Path("pydoc-markdown.yml").read_text() == static.DEFAULT_MKDOCS_CONFIG
        assert pyproject.read_text() == original_pyproject


def test_bootstrap_refuses_to_shadow_pyproject_config() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        pyproject = Path("pyproject.toml")
        original_pyproject = '[tool.pydoc-markdown.renderer]\ntype = "markdown"\n'
        pyproject.write_text(original_pyproject)

        result = runner.invoke(cli, ["--bootstrap", "mkdocs"])

        assert result.exit_code == 1
        assert result.output == "error: file already exists: 'pyproject.toml'\n"
        assert not Path("pydoc-markdown.yml").exists()
        assert pyproject.read_text() == original_pyproject


@pytest.mark.parametrize("existing_filename", ["pydoc-markdown.yml", "pydoc-markdown.yaml"])
def test_bootstrap_refuses_to_replace_existing_yaml_config(existing_filename: str) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        existing_config = Path(existing_filename)
        existing_config.write_text("sentinel\n")
        Path("pyproject.toml").write_text('[tool.poetry]\nname = "example"\n')

        result = runner.invoke(cli, ["--bootstrap", "mkdocs"])

        assert result.exit_code == 1
        assert result.output == f"error: file already exists: '{existing_filename}'\n"
        assert existing_config.read_text() == "sentinel\n"


def test_bootstrap_refuses_to_follow_dangling_yaml_symlink() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        config = Path("pydoc-markdown.yml")
        target = Path("target.yml")
        try:
            config.symlink_to(target)
        except (NotImplementedError, OSError) as exc:
            pytest.skip("symlinks are unavailable: {}".format(exc))

        result = runner.invoke(cli, ["--bootstrap", "mkdocs"])

        assert result.exit_code == 1
        assert result.output == "error: file already exists: 'pydoc-markdown.yml'\n"
        assert not target.exists()


def test_bootstrap_exclusive_creation_preserves_racing_file(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        config = Path("pydoc-markdown.yml")
        config.write_text("sentinel\n")
        real_lexists = os.path.lexists
        monkeypatch.setattr(
            os.path,
            "lexists",
            lambda filename: False if filename == "pydoc-markdown.yml" else real_lexists(filename),
        )

        result = runner.invoke(cli, ["--bootstrap", "mkdocs"])

        assert result.exit_code == 1
        assert result.output == "error: file already exists: 'pydoc-markdown.yml'\n"
        assert config.read_text() == "sentinel\n"


@pytest.mark.parametrize(
    "quick_options",
    [
        ["--module", "example"],
        ["--package", "example"],
        ["--search-path", "src"],
        ["--py2"],
        ["--py3"],
    ],
)
def test_quick_cli_options_warn_when_ignoring_implicit_config(
    monkeypatch: pytest.MonkeyPatch, quick_options: list[str]
) -> None:
    runner = CliRunner()
    loaded_config: list[object] = []

    def load(session: RenderSession) -> PydocMarkdown:
        loaded_config.append(session.config)
        return PydocMarkdown()

    monkeypatch.setattr(RenderSession, "load", load)
    monkeypatch.setattr(RenderSession, "render", lambda *_: [])

    with runner.isolated_filesystem():
        Path("pydoc-markdown.yml").write_text("renderer:\n  type: markdown\n")
        Path("pyproject.toml").write_text('[tool.pydoc-markdown.renderer]\ntype = "markdown"\n')

        result = runner.invoke(cli, quick_options)

    assert result.exit_code == 0, result.output
    assert loaded_config == [None]
    assert result.output == (
        "warning: quick CLI options disable implicit configuration loading; "
        "ignoring 'pydoc-markdown.yml'. Pass the configuration filename explicitly "
        "to apply CLI overrides to it.\n"
    )


@pytest.mark.parametrize(
    ("pyproject", "expected_output"),
    [
        ('[tool.poetry]\nname = "example"\n', ""),
        (
            '[tool.pydoc-markdown.renderer]\ntype = "markdown"\n',
            "warning: quick CLI options disable implicit configuration loading; "
            "ignoring 'pyproject.toml'. Pass the configuration filename explicitly "
            "to apply CLI overrides to it.\n",
        ),
    ],
)
def test_quick_cli_options_only_warn_for_configured_pyproject(
    monkeypatch: pytest.MonkeyPatch, pyproject: str, expected_output: str
) -> None:
    runner = CliRunner()
    loaded_config: list[object] = []

    def load(session: RenderSession) -> PydocMarkdown:
        loaded_config.append(session.config)
        return PydocMarkdown()

    monkeypatch.setattr(RenderSession, "load", load)
    monkeypatch.setattr(RenderSession, "render", lambda *_: [])

    with runner.isolated_filesystem():
        Path("pyproject.toml").write_text(pyproject)

        result = runner.invoke(cli, ["--module", "example"])

    assert result.exit_code == 0, result.output
    assert loaded_config == [None]
    assert result.output == expected_output
