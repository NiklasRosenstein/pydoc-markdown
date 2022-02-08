import pytest

from . import assert_processor_result
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor


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
  :return: A value
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

  **Returns**:

  A value
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

md_with_param = \
  '''
  **Arguments**:

  - `foo`: The value of foo
  - `bar`: The value of bar
  '''

doc_with_param_tmp = \
  '''
  :{pkey} foo: The value of foo
  :{pkey} bar: The value of bar
  '''

doc_with_param_type_adjacent_tmp = \
  '''
  :{pkey} foo: The value of foo
  :type foo: str
  :{pkey} bar: The value of bar
  :type bar: int
  '''

doc_with_param_type_mixed_tmp = \
  '''
  :{pkey} foo: The value of foo
  :type bar: int
  :type foo: str
  :{pkey} bar: The value of bar
  '''

md_with_param_type = \
  '''
  **Arguments**:
  
  - `foo` (`str`): The value of foo
  - `bar` (`int`): The value of bar
  '''

doc_with_param_return_tmp = \
  '''
  :param foo: Another value of foo
  :{rkey}: A description of return value
  '''

md_with_param_return = \
  '''
  **Arguments**:
  
  - `foo`: Another value of foo
  
  **Returns**:
  
  A description of return value
  '''

doc_with_raise_tmp = \
  '''
  :{rkey} KeyError: A key is missing
  '''

md_with_raise = \
  '''
  **Raises**:
  
  - `KeyError`: A key is missing
  '''

doc_with_multiline_param = \
  '''
  :param foolong: This parameter has a particularly long description
  that requires multiple lines.
  '''

md_with_multiline_param = \
  '''
  **Arguments**:

  - `foolong`: This parameter has a particularly long description
  that requires multiple lines.
  '''

@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
def test_sphinx_with_multiline_param(processor):
  assert_processor_result(processor, doc_with_multiline_param, md_with_multiline_param)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
@pytest.mark.parametrize("keyword", ["arg", "argument", "param", "parameter"])
def test_sphinx_with_param(processor, keyword):
  """Test sphinx docstrings with valid param keywords"""
  docstring = doc_with_param_tmp.format(pkey=keyword)
  assert_processor_result(processor, docstring, md_with_param)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
@pytest.mark.parametrize("keyword", ["arg", "argument", "param", "parameter"])
def test_sphinx_with_param_type_adjacent(processor, keyword):
  """Test sphinx docstrings with valid param keywords with types"""
  docstring = doc_with_param_type_adjacent_tmp.format(pkey=keyword)
  assert_processor_result(processor, docstring, md_with_param_type)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
@pytest.mark.parametrize("keyword", ["arg", "argument", "param", "parameter"])
def test_sphinx_with_param_type_mixed(processor, keyword):
  """Test sphinx docstrings with valid param keywords with types out of order"""
  docstring = doc_with_param_type_mixed_tmp.format(pkey=keyword)
  assert_processor_result(processor, docstring, md_with_param_type)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
@pytest.mark.parametrize("keyword", ["return", "returns"])
def test_sphinx_with_param_return(processor, keyword):
  """Test sphinx docstrings with valid return keywords"""
  docstring = doc_with_param_return_tmp.format(rkey=keyword)
  assert_processor_result(processor, docstring, md_with_param_return)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
@pytest.mark.parametrize("keyword", ["raise", "raises"])
def test_sphinx_with_raise(processor, keyword):
  """Test sphinx docstrings with valid raise keywords"""
  docstring = doc_with_raise_tmp.format(rkey=keyword)
  assert_processor_result(processor, docstring, md_with_raise)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
def test_sphinx_with_codeblocks(processor):
  """Test sphinx docstrings with codeblocks"""
  assert_processor_result(processor, docstring_with_codeblocks, md_with_codeblocks)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
def test_sphinx_with_param_type_returns_rtype(processor):
  """Test sphinx processor with param, type, returns, rtype keywords"""
  assert_processor_result(processor, docstring_with_param_type_returns_rtype, md_with_param_type_returns_rtype)
