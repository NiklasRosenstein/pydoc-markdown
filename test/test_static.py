import yaml

from pydoc_markdown.static import READTHEDOCS_FILES


def test_readthedocs_python_version_is_a_string() -> None:
    config = yaml.safe_load(READTHEDOCS_FILES[".readthedocs.yml"])

    assert config["python"]["version"] == "3.10"
