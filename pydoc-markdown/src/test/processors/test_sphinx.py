
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

  # check code blocks indentation
  assert_processor_result(processor or SphinxProcessor(),
  '''
  Code example:
  ```
  with a() as b:
    b()
  ```
  Implicit block:
      c()
  A longer one:
      d()
      with e() as f:
        f()
  ''',
  '''
  Code example:
  ```
  with a() as b:
    b()
  ```
  Implicit block:
      c()
  A longer one:
      d()
      with e() as f:
        f()
  ''')

  assert_processor_result(processor or SphinxProcessor(),
  '''
  :param foo: A foo value
  :type foo: str
  :type bar: int
  :param bar: A bar value
  :returns: Some eggs from foo and bar
  :rtype: str
  ''',
  '''
  **Arguments**:

  - `foo` (`str`): A foo value
  - `bar` (`int`): A bar value

  **Returns**:

  `str`: Some eggs from foo and bar
  ''')
