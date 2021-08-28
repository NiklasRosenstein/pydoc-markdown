
import dataclasses
import io
import textwrap
import typing as t
from pathlib import Path
import databind.json
import docspec
import pytest
from docspec_python import parse_python_module, ParserOptions
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from ..utils import Case, assert_text_equals, load_testcase, testcases_for


@dataclasses.dataclass
class MarkdownTestConfig:
  renderer: MarkdownRenderer = dataclasses.field(default_factory=MarkdownRenderer)
  filter: FilterProcessor = dataclasses.field(default_factory=FilterProcessor)
  parser: ParserOptions = dataclasses.field(default_factory=ParserOptions)


def load_string_as_module(
  filename: Path,
  code: str,
  module_name: t.Optional[str] = None,
  options: t.Optional[ParserOptions] = None
) -> docspec.Module:
  return parse_python_module(io.StringIO(code), str(filename), module_name or filename.stem, options)


def assert_code_as_markdown(source_code, markdown, full=False, parser_options=None, renderer_options=None):
  config = PydocMarkdown()

  # Init the settings in which we want to run the tests.
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
  modules = [parse_python_module(
    io.StringIO(textwrap.dedent(source_code)),
    filename='<string>',
    module_name='_inline',
    options=parser_options,
  )]

  config.process(modules)
  result = config.renderer.render_to_string(modules)
  assert_text_equals(result, textwrap.dedent(markdown))


@pytest.mark.parametrize('filename', testcases_for('renderers/markdown'))
def test_markdown_renderer(filename: str) -> None:
  case = load_testcase('renderers/markdown', filename)
  config = databind.json.load(case.config, MarkdownTestConfig)
  modules = [load_string_as_module(case.filename, case.code, options=config.parser)]
  config.filter.process(modules, None)
  SmartProcessor().process(modules, None)
  result = config.renderer.render_to_string(modules)
  assert_text_equals(result, case.output)
