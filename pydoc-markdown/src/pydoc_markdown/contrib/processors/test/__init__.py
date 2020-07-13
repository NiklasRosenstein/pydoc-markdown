
from pydoc_markdown.test.test_utils import assert_text_equals
import docspec
import textwrap


def assert_processor_result(processor, docstring, expected_output):
  module = docspec.Module(name='test', location=None, docstring=textwrap.dedent(docstring), members=[])
  processor.process([module], None)
  assert_text_equals(module.docstring, textwrap.dedent(expected_output))
