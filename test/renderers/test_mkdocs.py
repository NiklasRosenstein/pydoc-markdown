from databind.json import load

from pydoc_markdown.contrib.renderers.mkdocs import MkdocsRenderer
from pydoc_markdown.util.pages import Page


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
                    )
                ],
            ),
        ]
    )
