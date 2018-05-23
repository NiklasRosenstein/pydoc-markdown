import pytest

from pydocmd.document import Section
from pydocmd.restructuredtext import Preprocessor


@pytest.fixture
def preprocessor():
  return Preprocessor()


@pytest.fixture
def section():
  return Section(None)


def test_preprocess_section(preprocessor, section):
  section.content = '\n'.join([
    '```',
    'Param(foo, foo=bar)',
    '```',
    'This is the main documentation!',
    '',
    ' :param line1: The docs for line1',
    ':param line2: This docs for',
    'line2',
    ':return: This return',
    'can be multi-line!',
    ':raises ValueError: If something bad happens!'
  ])

  expected = '\n'.join([
    '```',
    'Param(foo, foo=bar)',
    '```',
    'This is the main documentation!',
    '',
    '**Arguments**:',
    '',
    '- `line1`: The docs for line1',
    '- `line2`: This docs for',
    'line2',
    '',
    '**Returns**:',
    '',
    'This return',
    'can be multi-line!',
    '',
    '**Raises**:',
    '',
    '- `ValueError`: If something bad happens!'
  ])

  preprocessor.preprocess_section(section)
  assert section.content == expected
