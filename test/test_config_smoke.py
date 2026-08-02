"""Runtime-only configuration loading smoke test for the supported Python boundaries."""

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer


def test_load_full_pipeline_config_without_unknown_fields() -> None:
    config = PydocMarkdown()
    config.load_config(
        {
            "loaders": [{"type": "python", "search_path": ["src/lib"]}],
            "processors": [{"type": "filter", "skip_empty_modules": True}],
            "renderer": {
                "type": "markdown",
                "filename": "docs/api.md",
                "render_toc": True,
            },
        }
    )

    assert config.unknown_fields == []
    assert len(config.loaders) == 1
    assert isinstance(config.loaders[0], PythonLoader)
    assert config.loaders[0].search_path == ["src/lib"]
    assert len(config.processors) == 1
    assert isinstance(config.processors[0], FilterProcessor)
    assert config.processors[0].skip_empty_modules is True
    assert isinstance(config.renderer, MarkdownRenderer)
    assert config.renderer.filename == "docs/api.md"
    assert config.renderer.render_toc is True


if __name__ == "__main__":
    test_load_full_pipeline_config_without_unknown_fields()
