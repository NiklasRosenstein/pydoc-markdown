
import unittest
from pydocmd.document import Section


class PreprocessorTest(unittest.TestCase):

  docstring_from = 'foo'
  trim_trailing_whitespace = False
  preprocessor = None
  code = None
  expected_docs = None

  def test_preprocessor(self):
    if type(self) is PreprocessorTest:
      raise unittest.SkipTest('Base class')

    scope = {}
    exec(compile(self.code, '<string>', 'exec'), scope)
    docstring = scope[self.docstring_from].__doc__

    section = Section(None)
    section.content = docstring
    self.preprocessor.preprocess_section(section)

    got = section.content.strip()
    expected = self.expected_docs.strip()
    if self.trim_trailing_whitespace:
      got = self._trim_trailing_whitespace(got)
      expected = self._trim_trailing_whitespace(expected)

    print(self.preprocessor)
    assert got == expected

  @staticmethod
  def _trim_trailing_whitespace(s):
    lines = s.split('\n')
    return '\n'.join(x.rstrip() for x in lines)
