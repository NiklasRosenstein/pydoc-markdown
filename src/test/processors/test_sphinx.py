
from . import assert_processor_result
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor


docstring_with_param_return = \
  '''
  :param s: A string.
  :param b: An int.
  :return: Something funny.
  '''

md_with_param_return = \
  '''
  **Arguments**:

  - `s`: A string.
  - `b`: An int.

  **Returns**:

  Something funny.
  '''

docstring_with_codeblocks = \
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
  '''

md_with_codeblocks = \
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
  '''

docstring_with_param_type_returns_rtype = \
  '''
  :param foo: A foo value
  :type foo: str
  :type bar: int
  :param bar: A bar value
  :returns: Some eggs from foo and bar
  :rtype: str
  '''

md_with_param_type_returns_rtype = \
  '''
  **Arguments**:

  - `foo` (`str`): A foo value
  - `bar` (`int`): A bar value

  **Returns**:

  `str`: Some eggs from foo and bar
  '''

docstring_with_param = \
  '''
  :param foo: The value of foo
  :param bar: The value of bar
  '''

md_with_param = \
  '''
  **Arguments**:

  - `foo`: The value of foo
  - `bar`: The value of bar
  '''


def test_sphinx_with_param_return(processor=None):
  """Test sphinx processor with param and return keywords."""
  if processor is None:
    processor = SphinxProcessor()
  assert_processor_result(processor, docstring_with_param_return, md_with_param_return)


def test_sphinx_with_codeblocks(processor=None):
  """Test sphinx processor with codeblocks"""
  if processor is None:
    processor = SphinxProcessor()
  assert_processor_result(processor, docstring_with_codeblocks, md_with_codeblocks)


def test_sphinx_with_param_type_returns_rtype(processor=None):
  """Test sphinx processor with param, type, returns, rtype keywords"""
  if processor is None:
    processor = SphinxProcessor()
  assert_processor_result(processor, docstring_with_param_type_returns_rtype, md_with_param_type_returns_rtype)


def test_sphinx_with_param(processor=None):
  """Test sphinx processor with only param keyword."""
  if processor is None:
    processor = SphinxProcessor()
  assert_processor_result(processor, docstring_with_param, md_with_param)
