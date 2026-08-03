import pytest
from docstring_parser import DocstringStyle

from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor

from . import assert_processor_result

docstring_with_codeblocks = """
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
  """

md_with_codeblocks = """
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
  """

docstring_with_param_type_returns_rtype = """
  :param foo: A foo value
  :type foo: str
  :type bar: int
  :param bar: A bar value
  :returns: Some eggs from foo and bar
  :rtype: str
  """

md_with_param_type_returns_rtype = """
  **Arguments**:

  - `foo` (`str`): A foo value
  - `bar` (`int`): A bar value

  **Returns**:

  `str`: Some eggs from foo and bar
  """

numpy_docstring = """
  Compute a result.

  Parameters
  ----------
  x : int
      Input value.
  label : str, optional
      Label for the result.

  Returns
  -------
  bool
      Whether the operation succeeded.

  Raises
  ------
  ValueError
      If x is negative.
  """

numpy_markdown = """
  Compute a result.

  **Arguments**:

  - `x` (`int`): Input value.
  - `label` (`str`): Label for the result.

  **Raises**:

  - `ValueError`: If x is negative.

  **Returns**:

  `bool`: Whether the operation succeeded.
  """

numpy_docstring_with_additional_sections = """
  Generate results.

  Yields
  ------
  int
      The next value.

  Returns
  -------
  count : int
      Number of results.
  label : str
      Result label.

  Examples
  --------
  >>> list(generate())
  [1]

  Notes
  -----
  Results are generated lazily.
  """

numpy_additional_sections_markdown = """
  Generate results.

  **Returns**:

  - `count` (`int`): Number of results.
  - `label` (`str`): Result label.

  **Yields**:

  `int`: The next value.

  **Examples**:

  >>> list(generate())
  [1]

  **Notes**:

  Results are generated lazily.
  """

four_space_indented_code_block = """
  Example:

      >>> url = URL('https://foo.bar')
      >>> print(url)
      https://foo.bar

  :param url: Link to a remote file.
  """

four_space_indented_code_block_markdown = """
  Example:

      >>> url = URL('https://foo.bar')
      >>> print(url)
      https://foo.bar

  **Arguments**:

  - `url`: Link to a remote file.
  """

md_with_param = """
  **Arguments**:

  - `foo`: The value of foo
  - `bar`: The value of bar
  """

doc_with_param_tmp = """
  :{pkey} foo: The value of foo
  :{pkey} bar: The value of bar
  """

doc_with_param_type_adjacent_tmp = """
  :{pkey} foo: The value of foo
  :type foo: str
  :{pkey} bar: The value of bar
  :type bar: int
  """

doc_with_param_type_mixed_tmp = """
  :{pkey} foo: The value of foo
  :type bar: int
  :type foo: str
  :{pkey} bar: The value of bar
  """

md_with_param_type = """
  **Arguments**:
  
  - `foo` (`str`): The value of foo
  - `bar` (`int`): The value of bar
  """

doc_with_param_return_tmp = """
  :param foo: Another value of foo
  :{rkey}: A description of return value
  """

md_with_param_return = """
  **Arguments**:
  
  - `foo`: Another value of foo
  
  **Returns**:
  
  A description of return value
  """

doc_with_raise_tmp = """
  :{rkey} KeyError: A key is missing
  """

md_with_raise = """
  **Raises**:
  
  - `KeyError`: A key is missing
  """

doc_with_multiline_param = """
  :param foolong: This parameter has a particularly long description
  that requires multiple lines.
  """

md_with_multiline_param = """
  **Arguments**:

  - `foolong`: This parameter has a particularly long description
  that requires multiple lines.
  """


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


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
def test_numpy_docstring(processor):
    assert_processor_result(processor, numpy_docstring, numpy_markdown)


def test_explicit_numpy_docstring_style():
    processor = SphinxProcessor(style=DocstringStyle.NUMPYDOC)
    assert_processor_result(processor, numpy_docstring, numpy_markdown)


@pytest.mark.parametrize("processor", [SphinxProcessor(), SmartProcessor()])
def test_numpy_additional_sections_are_preserved(processor):
    assert_processor_result(processor, numpy_docstring_with_additional_sections, numpy_additional_sections_markdown)


@pytest.mark.parametrize(
    "processor",
    [SphinxProcessor(), SphinxProcessor(style=DocstringStyle.REST), SmartProcessor()],
)
def test_four_space_indented_code_block(processor):
    """Regression test for the exact report in #259."""

    assert_processor_result(processor, four_space_indented_code_block, four_space_indented_code_block_markdown)
