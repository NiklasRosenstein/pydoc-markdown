import typing as t

import docspec

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.main import RenderSession


class WatchRenderer(Renderer):
    def render(self, modules: t.List[docspec.Module]) -> None:
        pass

    def get_watch_files(self) -> t.Iterable[str]:
        return ["page-source.md"]


class DefaultRenderer(Renderer):
    def render(self, modules: t.List[docspec.Module]) -> None:
        pass


def test__RenderSession__render_includes_renderer_watch_files() -> None:
    config = PydocMarkdown(loaders=[], processors=[], renderer=WatchRenderer())

    assert RenderSession(config=None).render(config) == ["page-source.md"]


def test__Renderer__does_not_add_watch_files_by_default() -> None:
    assert list(DefaultRenderer().get_watch_files()) == []
