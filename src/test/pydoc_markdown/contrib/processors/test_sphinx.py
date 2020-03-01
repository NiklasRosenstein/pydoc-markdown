
from . import assert_processor_result
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor
import textwrap


def test_sphinx_processor():
  assert_processor_result(SphinxProcessor(),
  '''
  :param s: A string.
  :param b: An int.
  :return: Something funny.
  ''',
  '''
  **Arguments**:

  - `s`: A string.
  - `b`: An int.

  **Returns**:

  Something funny.
  ''')
