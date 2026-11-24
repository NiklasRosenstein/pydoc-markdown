import dataclasses
import io
import textwrap
import typing as t
from pathlib import Path

import databind.json
import docspec
import pytest
from docspec_python import ParserOptions, parse_python_module

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Processor

from ..utils import assert_text_equals, get_testcases_for, load_testcase


@dataclasses.dataclass
class MarkdownTestConfig:
    renderer: MarkdownRenderer = dataclasses.field(default_factory=MarkdownRenderer)
    filter: FilterProcessor = dataclasses.field(default_factory=FilterProcessor)
    parser: ParserOptions = dataclasses.field(default_factory=ParserOptions)
    processor: Processor = dataclasses.field(default_factory=SmartProcessor)

    def init(self, context: Context) -> None:
        self.renderer.init(context)
        self.filter.init(context)
        self.processor.init(context)


def load_string_as_module(
    filename: Path, code: str, module_name: t.Optional[str] = None, options: t.Optional[ParserOptions] = None
) -> docspec.Module:
    return parse_python_module(io.StringIO(code), str(filename), module_name or filename.stem, options)


def assert_code_as_markdown(source_code, markdown, full=False, parser_options=None, renderer_options=None):
    config = PydocMarkdown()

    # Init the settings in which we want to run the tests.
    assert isinstance(config.render, MarkdownRenderer)
    config.init(Context("."))
    config.renderer.insert_header_anchors = False
    config.renderer.add_member_class_prefix = False
    config.renderer.render_toc = False
    config.renderer.render_module_header = full
    for key, value in (renderer_options or {}).items():
        assert hasattr(config.renderer, key), key
        setattr(config.renderer, key, value)
    filter_processor = next(x for x in config.processors if isinstance(x, FilterProcessor))
    filter_processor.documented_only = False

    # Load the source code as a module.
    modules = [
        parse_python_module(
            io.StringIO(textwrap.dedent(source_code)),
            filename="<string>",
            module_name="_inline",
            options=parser_options,
        )
    ]

    config.process(modules)
    result = config.renderer.render_to_string(modules)
    assert_text_equals(result, textwrap.dedent(markdown))


@pytest.mark.parametrize("filename", get_testcases_for("renderers/markdown"))
def test_markdown_renderer(filename: str) -> None:
    case = load_testcase("renderers/markdown", filename)
    config = databind.json.load(case.config, MarkdownTestConfig)
    config.init(Context("."))
    modules = [load_string_as_module(case.filename, case.code, options=config.parser)]
    config.filter.process(modules, None)
    config.processor.process(modules, None)
    result = config.renderer.render_to_string(modules)
    assert_text_equals(result, case.output)


def test_markdown_renderer_page_title_fallback() -> None:
    renderer = databind.json.load(
        {"render_page_title": True, "page_title": "API Documentation"},
        MarkdownRenderer,
    )

    assert renderer.render_to_string([]) == "# API Documentation\n\n"


def test_markdown_renderer_explicit_page_title_takes_precedence() -> None:
    renderer = MarkdownRenderer(render_page_title=True, page_title="API Documentation")
    fp = io.StringIO()

    renderer.render_single_page(fp, [], "Specific Page")

    assert fp.getvalue() == "# Specific Page\n\n"


REFERENCE_LINKS_MODULE = '''
"""Module docstring. See the [spec].

[spec]: https://spec.example
"""

def a():
    """A uses [docs][ref], [ref][] and [ref], plus [spec] from the module.

    [ref]: https://a.example
    """

def b():
    """B uses [ref], an inline [link](https://inline.example), `[ref]` and:

    ```
    [ref]
    ```

    [ref]: https://b.example
    """

def c():
    """C defines a [unique] label.

    [unique]: https://c.example
    """
'''


def _render_page(code: str, **options: t.Any) -> str:
    module = load_string_as_module(Path("refs.py"), textwrap.dedent(code))
    renderer = MarkdownRenderer(
        insert_header_anchors=False, render_module_header=False, signature_code_block=False, **options
    )
    renderer.init(Context("."))
    return renderer.render_to_string([module])


def test_markdown_renderer_namespaces_duplicate_reference_links() -> None:
    result = _render_page(REFERENCE_LINKS_MODULE)

    # Both definitions of `ref` are renamed, and so are all reference forms that use them.
    assert "A uses [docs][refs.a--ref], [ref][refs.a--ref] and [ref][refs.a--ref]" in result
    assert "[refs.a--ref]: https://a.example" in result
    assert "B uses [ref][refs.b--ref], an inline [link](https://inline.example), `[ref]` and:" in result
    assert "```\n[ref]\n```" in result
    assert "[refs.b--ref]: https://b.example" in result
    # A label that is defined only once on the page doesn't need to be renamed.
    assert "C defines a [unique] label.\n\n[unique]: https://c.example" in result


def test_markdown_renderer_reference_link_namespacing_can_be_disabled() -> None:
    assert "[ref]: https://b.example" in _render_page(REFERENCE_LINKS_MODULE, namespace_reference_links=False)


def test_markdown_renderer_keeps_labels_that_another_docstring_relies_on() -> None:
    result = _render_page(
        '''
        def a():
            """[x]

            [x]: https://a.example
            """

        def b():
            """[x]

            [x]: https://b.example
            """

        def c():
            """Relies on the first definition of [x]."""
        '''
    )

    assert "[x]: https://a.example" in result
    assert "[x]: https://b.example" in result
    assert "Relies on the first definition of [x]." in result


@pytest.mark.parametrize(
    ("usage", "expected"),
    [
        pytest.param("[the long\n    text][x]", "[the long\ntext][refs.a--x]", id="wrapped-text"),
        pytest.param("[`Foo`][x]", "[`Foo`][refs.a--x]", id="code-span-text"),
        pytest.param("[![img](x.png)][x]", "[![img](x.png)][refs.a--x]", id="image-text"),
        pytest.param("See [x]: nice", "See [x][refs.a--x]: nice", id="shortcut-followed-by-colon"),
    ],
)
def test_markdown_renderer_namespaces_reference_link_forms(usage: str, expected: str) -> None:
    code = '''
def a():
    """{usage}

    [x]: https://a.example
    """

def b():
    """[x]

    [x]: https://b.example
    """
'''
    result = _render_page(code.replace("{usage}", usage))

    assert expected in result
    assert "[refs.a--x]: https://a.example" in result


def test_markdown_renderer_skips_labels_in_indented_code() -> None:
    result = _render_page(
        '''
        def a():
            """See [1].

                >>> x[1]

            [1]: https://a.example
            """

        def b():
            """See [1].

            [1]: https://b.example
            """
        '''
    )

    assert ">>> x[1]\n" in result
    assert "[1]: https://a.example" in result
    assert "[1][refs.b--1]" in result


def test_markdown_renderer_namespaces_same_named_objects_uniquely() -> None:
    result = _render_page(
        '''
        def a():
            """[x]

            [x]: https://first.example
            """

        def a():
            """[x]

            [x]: https://second.example
            """
        '''
    )

    assert "[refs.a--x]: https://first.example" in result
    assert "[refs.a--x-2]: https://second.example" in result


def test_markdown_renderer_namespaces_individually_rendered_objects_only_when_enabled() -> None:
    module = load_string_as_module(Path("refs.py"), REFERENCE_LINKS_MODULE)

    def render(**options: t.Any) -> str:
        renderer = MarkdownRenderer(insert_header_anchors=False, render_module_header=False, **options)
        renderer.init(Context("."))
        fp = io.StringIO()
        renderer.render_object(fp, module.members[2], {})
        renderer.render_object(fp, module, {})
        return fp.getvalue()

    assert "C defines a [unique] label." in render()

    result = render(namespace_reference_links_in_objects=True)
    # The rest of the page is unknown, so even a label that is unique within the rendered object is renamed.
    assert "C defines a [unique][refs.c--unique] label.\n\n[refs.c--unique]: https://c.example" in result
    # A definition that a member relies on is still left alone.
    assert "plus [spec] from the module" in result
    assert "[spec]: https://spec.example" in result
