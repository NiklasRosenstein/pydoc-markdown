
from . import test_google, test_pydocmd, test_sphinx
from pydoc_markdown.contrib.processors.smart import SmartProcessor


def test_google_style():
  test_google.test_google_processor(SmartProcessor())


def test_sphinx_style():
  test_sphinx.test_sphinx_processor(SmartProcessor())


def test_pydocmd_style():
  test_pydocmd.test_pydocmd_processor(SmartProcessor())
