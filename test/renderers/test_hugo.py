from databind.json import load

from pydoc_markdown.contrib.renderers.hugo import HugoPage, HugoRenderer
from pydoc_markdown.interfaces import Context
from pydoc_markdown.util.pages import Pages


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
                        "exclude": ["package.internal"],
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
                        exclude=["package.internal"],
                    )
                ],
            ),
        ]
    )


def test_hugo_renderer_filters_page_modules_once(tmp_path, monkeypatch) -> None:
    page = HugoPage(title="API", contents=["*"])
    filtered_modules = page.filtered_modules
    calls = 0

    def count_filtered_modules(modules):
        nonlocal calls
        calls += 1
        return filtered_modules(modules)

    monkeypatch.setattr(page, "filtered_modules", count_filtered_modules)
    renderer = HugoRenderer(build_directory=str(tmp_path), pages=Pages([page]))
    renderer.init(Context(directory=str(tmp_path)))

    renderer.render([])

    assert calls == 1


def test_hugo_renderer_watches_nested_page_sources(tmp_path) -> None:
    absolute_source = str(tmp_path / "absolute.md")
    renderer = HugoRenderer(
        pages=Pages(
            [
                HugoPage(
                    title="Parent",
                    children=[
                        HugoPage(title="Relative", source="docs/../relative.md"),
                        HugoPage(title="Absolute", source=absolute_source),
                    ],
                )
            ]
        )
    )
    renderer.init(Context(directory=str(tmp_path)))

    assert list(renderer.get_watch_files()) == [str(tmp_path / "relative.md"), absolute_source]
