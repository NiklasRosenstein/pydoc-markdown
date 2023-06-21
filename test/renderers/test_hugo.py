from databind.json import load

from pydoc_markdown.contrib.renderers.hugo import HugoPage, HugoRenderer
from pydoc_markdown.util.pages import Page


def test_deserialize_hugo_renderer() -> None:
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
    renderer = load(payload, HugoRenderer)
    assert renderer == HugoRenderer(
        pages=[
            HugoPage(
                title="Home",
                name="index",
                source="README.md",
                children=[
                    HugoPage(
                        title="Child",
                        name="child",
                        source="child.md",
                    )
                ],
            ),
        ]
    )
