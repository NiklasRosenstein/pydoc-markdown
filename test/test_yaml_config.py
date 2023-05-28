"""
Test loding the YAML configuration format for Pydoc Markdown.
"""

from pytest import raises

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.renderers.docusaurus import CustomizedMarkdownRenderer, DocusaurusRenderer
from pydoc_markdown.contrib.renderers.hugo import HugoConfig, HugoRenderer
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer


def test__PydocMarkdown__load_config__empty_input() -> None:
    pydoc_markdown = PydocMarkdown()
    pydoc_markdown.load_config({})
    assert pydoc_markdown == PydocMarkdown()


def test__PydocMarkdown__load_config__can_deserialize_markdown_config_from_entrypoint_name() -> None:
    pydoc_markdown = PydocMarkdown()
    pydoc_markdown.load_config(
        {
            "renderer": {
                "type": "markdown",
                "render_toc": True,
            },
        }
    )
    assert pydoc_markdown == PydocMarkdown(
        renderer=MarkdownRenderer(
            render_toc=True,
        )
    )


def test__PydocMarkdown__load_config__can_deserialize_markdown_config_from_import_name() -> None:
    pydoc_markdown = PydocMarkdown()
    pydoc_markdown.load_config(
        {
            "renderer": {
                "type": "pydoc_markdown.contrib.renderers.markdown.MarkdownRenderer",
                "render_toc": True,
            },
        }
    )
    assert pydoc_markdown == PydocMarkdown(
        renderer=MarkdownRenderer(
            render_toc=True,
        )
    )


def test__PydocMarkdown__load_config__cannot_deserialize_markdown_config_from_bad_import_name() -> None:
    pydoc_markdown = PydocMarkdown()
    with raises(AttributeError):
        pydoc_markdown.load_config(
            {
                "renderer": {
                    "type": "pydoc_markdown.contrib.renderers.markdown.MarkdownRenderererer",
                    "render_toc": True,
                },
            }
        )


def test__PydocMarkdown__load_config__can_deserialize_hugo_with_remainder_values() -> None:
    pydoc_markdown = PydocMarkdown()
    pydoc_markdown.load_config(
        {
            "renderer": {
                "type": "hugo",
                "config": {
                    "title": "My Docs",
                    "theme": "antarctica",
                    "foo": "bar",
                },
            },
        }
    )
    assert pydoc_markdown == PydocMarkdown(
        renderer=HugoRenderer(
            config=HugoConfig(
                title="My Docs",
                theme="antarctica",
                additional_options={
                    "foo": "bar",
                },
            ),
        )
    )


def test__PydocMarkdown__load_config__can_deserialize_docusaurus_renderer() -> None:
    pydoc_markdown = PydocMarkdown()
    pydoc_markdown.load_config(
        {
            "renderer": {
                "type": "docusaurus",
                "markdown": {
                    "encoding": "foobar",
                },
            },
        }
    )
    assert pydoc_markdown == PydocMarkdown(
        renderer=DocusaurusRenderer(
            markdown=CustomizedMarkdownRenderer(
                encoding="foobar",
            )
        )
    )
    assert isinstance(pydoc_markdown.renderer, DocusaurusRenderer)
    assert isinstance(pydoc_markdown.renderer.markdown, CustomizedMarkdownRenderer)
