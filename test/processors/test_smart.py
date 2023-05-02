from pydoc_markdown.contrib.processors.smart import SmartProcessor

from . import test_google, test_pydocmd, test_sphinx

# Testing the SmartProcessor with sphinx docstrings has moved to the test_sphinx.py module


def test_google_style():
    test_google.test_google_processor(SmartProcessor())


def test_pydocmd_style():
    test_pydocmd.test_pydocmd_processor(SmartProcessor())
