
import textwrap
from .utils import PreprocessorTest
from .test_rst_preprocessor import RSTPreprocessorTest
from .test_google_preprocessor import GooglePreprocessorTest
from pydocmd.preprocessors.rst import Preprocessor


class SmartRSTPreprocessorTest(RSTPreprocessorTest):
  preprocessor = Preprocessor()


class SmartGooglePreprocessorTest(GooglePreprocessorTest):
  preprocessor = Preprocessor()
