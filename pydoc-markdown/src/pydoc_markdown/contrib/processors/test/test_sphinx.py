
from . import assert_processor_result
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor


def test_sphinx_processor(processor=None):
  assert_processor_result(processor or SphinxProcessor(),
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
