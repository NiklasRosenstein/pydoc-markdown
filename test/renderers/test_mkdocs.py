import pytest
from databind.json import load

from pydoc_markdown.contrib.renderers.mkdocs import MkdocsRenderer
from pydoc_markdown.interfaces import Context
from pydoc_markdown.util.pages import Page, Pages


def test_deserialize_mkdocs_renderer() -> None:
    payload = {
        "pages": [
            {
                "title": "Home",
                "name": "index",
                "source": "README.md",
                "children": [
                    {
                        "title": "Child",
                        "name": "child",
                        "source": "child.md",
                        "exclude": ["package.internal"],
                    }
                ],
            }
        ]
    }
    renderer = load(payload, MkdocsRenderer)
    assert renderer == MkdocsRenderer(
        pages=[
            Page(
                title="Home",
                name="index",
                source="README.md",
                children=[
                    Page(
                        title="Child",
                        name="child",
                        source="child.md",
                        exclude=["package.internal"],
                    )
                ],
            ),
        ]
    )


def test_mkdocs_renderer_watches_nested_page_sources(tmp_path) -> None:
    absolute_source = str(tmp_path / "absolute.md")
    renderer = MkdocsRenderer(
        pages=Pages(
            [
                Page(
                    title="Parent",
                    children=[
                        Page(title="Relative", source="docs/../relative.md"),
                        Page(title="Absolute", source=absolute_source),
                    ],
                )
            ]
        )
    )
    renderer.init(Context(directory=str(tmp_path)))

    assert list(renderer.get_watch_files()) == [str(tmp_path / "relative.md"), absolute_source]


def test_mkdocs_renderer_watch_files_requires_initialization() -> None:
    with pytest.raises(RuntimeError, match="initialized"):
        list(MkdocsRenderer().get_watch_files())
