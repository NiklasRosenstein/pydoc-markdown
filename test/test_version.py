from pathlib import Path

import tomli

import pydoc_markdown


def test_version_matches_pyproject() -> None:
    pyproject = tomli.loads((Path(__file__).parent.parent / "pyproject.toml").read_text())
    assert pydoc_markdown.__version__ == pyproject["project"]["version"]
