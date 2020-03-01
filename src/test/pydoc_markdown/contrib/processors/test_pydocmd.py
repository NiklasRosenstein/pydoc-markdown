
from pydoc_markdown.contrib.processors.pydocmd import PydocmdProcessor
from pydoc_markdown.reflection import Object, ModuleGraph
from test.pydoc_markdown.utils import assert_text_equals
import textwrap


def assert_processed_result(docstring, expected_output):
  obj = Object(None, name='test', docstring=textwrap.dedent(docstring))
  graph = ModuleGraph()
  graph.add_module(obj)
  processor = PydocmdProcessor()
  processor.process(graph)
  assert_text_equals(obj.docstring, textwrap.dedent(expected_output))


def test_arguments():
  assert_processed_result(
  '''
  # Arguments
  s (str): A string.
  b (int): An int.
  ''',
  '''
  __Arguments__

  - __s__ (`str`): A string.
  - __b__ (`int`): An int.
  ''')
