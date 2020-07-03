# empty


from test.pydoc_markdown.utils import assert_text_equals
import docspec
import textwrap


def assert_processor_result(processor, docstring, expected_output):
  module = docspec.Module('test', None, textwrap.dedent(docstring), [])
  processor.process([module], None)
  assert_text_equals(module.docstring, textwrap.dedent(expected_output))
