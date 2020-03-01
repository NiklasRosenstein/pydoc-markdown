
from . import assert_processor_result
from pydoc_markdown.contrib.processors.pydocmd import PydocmdProcessor
import textwrap


def test_pydocmd_processor(processor=None):
  assert_processor_result(processor or PydocmdProcessor(),
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
