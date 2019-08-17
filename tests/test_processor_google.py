
import textwrap
from .utils import PreprocessorTest
from pydocmd.preprocessors.google import Preprocessor


class GooglePreprocessorTest(PreprocessorTest):

  # NOTE: The google preprocessor does not produce clean line endings.
  trim_trailing_whitespace = True

  preprocessor = Preprocessor()

  code = textwrap.dedent('''
    def foo(a, b):
      """Foo a and b.

      This is a function that computes a foo combination of two integers.

      Args:
        a (int): The integer A.
        b (int): The integer B.

      Returns:
        int: Foo combination of  ``a`` and ``b``.
      """
  ''')

  expected_docs = textwrap.dedent('''
    Foo a and b.

    This is a function that computes a foo combination of two integers.

    **Arguments**:

    - `a` _int_ - The integer A.
    - `b` _int_ - The integer B.


    **Returns**:

    - `int` - Foo combination of  ``a`` and ``b``.
  ''')
