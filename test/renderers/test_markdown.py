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
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer, _list_content_indent
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


def test_markdown_renderer_preserves_unique_reference_labels() -> None:
    module = load_string_as_module(
        Path("unique_reference.py"),
        '''def func():
    """Links to [example][0].

    [0]: https://example.com
    """
''',
    )
    renderer = MarkdownRenderer(insert_header_anchors=False, render_module_header=False, signature_code_block=False)
    renderer.init(Context("."))

    assert renderer.render_to_string([module]) == (
        "#### func\n\nLinks to [example][0].\n\n[0]: https://example.com\n\n"
    )


def test_markdown_renderer_namespaces_separately_rendered_objects() -> None:
    module = load_string_as_module(
        Path("separate_objects.py"),
        '''def a():
    """Links to [A][0].

    [0]: https://a.example
    """

def b():
    """Links to [B][0].

    [0]: https://b.example
    """
''',
    )
    renderer = MarkdownRenderer(insert_header_anchors=False, render_module_header=False, signature_code_block=False)
    renderer.init(Context("."))
    fp = io.StringIO()

    renderer.render_object(fp, module.members[0], {})
    renderer.render_object(fp, module.members[1], {})

    assert "[A][pydoc-separate_objects.a-0]" in fp.getvalue()
    assert "[pydoc-separate_objects.a-0]: https://a.example" in fp.getvalue()
    assert "[B][pydoc-separate_objects.b-0]" in fp.getvalue()
    assert "[pydoc-separate_objects.b-0]: https://b.example" in fp.getvalue()


def test_markdown_list_content_indentation_uses_visual_columns() -> None:
    assert _list_content_indent("-\tcontent") == 4
    assert _list_content_indent("1.\tcontent") == 4


def test_markdown_renderer_analyzes_escaped_docstrings() -> None:
    module = load_string_as_module(
        Path("escaped_html.py"),
        '''def a():
    """<div>
    [x]
    </div>

    [x]: https://a.example
    """

def b():
    """<div>
    [x]
    </div>

    [x]: https://b.example
    """
''',
    )
    renderer = MarkdownRenderer(
        insert_header_anchors=False,
        render_module_header=False,
        signature_code_block=False,
        escape_html_in_docstring=True,
    )
    renderer.init(Context("."))

    result = renderer.render_to_string([module])

    assert "&lt;div&gt;\n[x][pydoc-escaped_html.a-x]\n&lt;/div&gt;" in result
    assert "[pydoc-escaped_html.a-x]: https://a.example" in result
    assert "&lt;div&gt;\n[x][pydoc-escaped_html.b-x]\n&lt;/div&gt;" in result
    assert "[pydoc-escaped_html.b-x]: https://b.example" in result


def test_markdown_renderer_validates_reference_syntax_boundaries() -> None:
    module = load_string_as_module(
        Path("reference_syntax.py"),
        r'''def a():
    r"""A quote in a bare destination stays intact: [link](foo'bar[bare]).

    [quote]: https://quote-a.example
    > "A different-container usage [quote]"

    Invalid inline HTML exposes its [html] shortcut: <tag [html]>.

    An [invalid] definition remains plain text.

    [bare]: https://bare-a.example
    [html]: https://html-a.example
    [invalid]: foo\ bar
    """

def b():
    r"""A quote in a bare destination stays intact: [link](foo'bar[bare]).

    [quote]: https://quote-b.example
    > "A different-container usage [quote]"

    Invalid inline HTML exposes its [html] shortcut: <tag [html]>.

    An [invalid] definition remains plain text.

    [bare]: https://bare-b.example
    [html]: https://html-b.example
    [invalid]: foo\ bar
    """
''',
    )
    renderer = MarkdownRenderer(insert_header_anchors=False, render_module_header=False, signature_code_block=False)
    renderer.init(Context("."))

    result = renderer.render_to_string([module])

    assert result.count("[link](foo'bar[bare])") == 2
    assert "[bare]: https://bare-a.example" in result
    assert "[bare]: https://bare-b.example" in result
    assert '> "A different-container usage [quote][pydoc-reference_syntax.a-quote]"' in result
    assert "[pydoc-reference_syntax.a-quote]: https://quote-a.example" in result
    assert "<tag [html][pydoc-reference_syntax.a-html]>" in result
    assert "[pydoc-reference_syntax.a-html]: https://html-a.example" in result
    assert "An [invalid] definition remains plain text." in result
    assert "[invalid]: foo\\ bar" in result
