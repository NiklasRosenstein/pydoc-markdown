import textwrap
from test.utils import assert_text_equals

import docspec


def assert_processor_result(processor, docstring, expected_output):
    loc = docspec.Location("<string>", 0)
    module = docspec.Module(
        name="test", location=loc, docstring=docspec.Docstring(loc, textwrap.dedent(docstring)), members=[]
    )
    processor.process([module], None)
    assert module.docstring
    print(module.docstring.content)
    assert_text_equals(module.docstring.content, textwrap.dedent(expected_output))
