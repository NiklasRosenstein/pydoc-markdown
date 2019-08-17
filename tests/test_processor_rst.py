
import textwrap
from .utils import PreprocessorTest
from pydocmd.preprocessors.rst import Preprocessor


class RSTPreprocessorTest(PreprocessorTest):

  preprocessor = Preprocessor()

  code = textwrap.dedent('''
    def foo(a, b):
      """
      ```
      Param(foo, foo=bar)
      ```
      This is the main documentation!

      :param line1: The docs for line1
      :param line2: This docs for
      line2
      :return: This return
      can be multi-line!
      :raises ValueError: If something bad happens!
      """
  ''')

  expected_docs = textwrap.dedent('''
      ```
      Param(foo, foo=bar)
      ```
      This is the main documentation!

    **Arguments**:

    - `line1`: The docs for line1
    - `line2`: This docs for
      line2

    **Returns**:

    This return
      can be multi-line!

    **Raises**:

    - `ValueError`: If something bad happens!
  ''')
