# empty


from pydoc_markdown.reflection import Object, ModuleGraph
from test.pydoc_markdown.utils import assert_text_equals
import textwrap


def assert_processor_result(processor, docstring, expected_output):
  obj = Object(None, name='test', docstring=textwrap.dedent(docstring))
  graph = ModuleGraph()
  graph.add_module(obj)
  processor.process(graph)
  assert_text_equals(obj.docstring, textwrap.dedent(expected_output))
