import yaml

from pydoc_markdown.static import READTHEDOCS_FILES


def test_readthedocs_config_uses_build_commands() -> None:
    config = yaml.safe_load(READTHEDOCS_FILES[".readthedocs.yaml"])

    assert config["version"] == 2
    assert config["build"]["tools"]["python"] == "3.12"
    assert "python" not in config  # The `python.version` key was removed by Read the Docs.
    assert any("--site-dir" in command for command in config["build"]["commands"])
