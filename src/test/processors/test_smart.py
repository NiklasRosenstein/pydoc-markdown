
from . import test_google, test_pydocmd, test_sphinx
from pydoc_markdown.contrib.processors.smart import SmartProcessor


def test_google_style():
  test_google.test_google_processor(SmartProcessor())


def test_sphinx_style():
  # Dynamically call all tests within the test_sphinx module
  test_sphinx_attr_names = dir(test_sphinx)
  for attr_name in test_sphinx_attr_names:
    sphinx_attr = getattr(test_sphinx, attr_name)
    if callable(sphinx_attr) and attr_name.startswith("test"):
      sphinx_attr(SmartProcessor())


def test_pydocmd_style():
  test_pydocmd.test_pydocmd_processor(SmartProcessor())
