"""
Test case for issue #125: Uniquify Markdown anchor references
"""
import io
import textwrap

import docspec
from docspec_python import parse_python_module

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context


def assert_code_as_markdown(source_code, markdown):
    """Helper to test code rendering."""
    config = PydocMarkdown()

    # Init the settings.
    assert isinstance(config.renderer, MarkdownRenderer)
    config.init(Context("."))
    config.renderer.insert_header_anchors = False
    config.renderer.add_member_class_prefix = False
    config.renderer.render_toc = False
    config.renderer.render_module_header = False
    config.renderer.signature_code_block = False  # Disable signature code blocks for cleaner tests
    filter_processor = next(x for x in config.processors if isinstance(x, FilterProcessor))
    filter_processor.documented_only = False

    # Load the source code as a module.
    modules = [
        parse_python_module(
            io.StringIO(textwrap.dedent(source_code)),
            filename="<string>",
            module_name="_inline",
            options=None,
        )
    ]

    config.process(modules)
    result = config.renderer.render_to_string(modules)

    expected = textwrap.dedent(markdown).strip()
    actual = result.strip()

    if expected != actual:
        print("EXPECTED:")
        print(expected)
        print("\nACTUAL:")
        print(actual)

    assert expected == actual


def test_duplicate_markdown_references_are_uniquified():
    """Test that duplicate reference-style link IDs in different docstrings are made unique."""
    source = """
    def a():
        \"\"\"Links to [a][0].

        [0]: https://a.org
        \"\"\"
        pass

    def b():
        \"\"\"Links to [b][0].

        [0]: https://b.org
        \"\"\"
        pass
    """

    # After the fix, references should be uniquified with object name prefix
    expected = """
    #### a

    Links to [a][a-0].

    [a-0]: https://a.org

    #### b

    Links to [b][b-0].

    [b-0]: https://b.org
    """

    assert_code_as_markdown(source, expected)


def test_all_references_are_prefixed():
    """Test that all reference IDs are prefixed for consistency and guaranteed uniqueness."""
    source = """
    def a():
        \"\"\"Links to [a][a_link].

        [a_link]: https://a.org
        \"\"\"
        pass

    def b():
        \"\"\"Links to [b][b_link].

        [b_link]: https://b.org
        \"\"\"
        pass
    """

    # All references are prefixed with the object name for guaranteed uniqueness
    expected = """
    #### a

    Links to [a][a-a_link].

    [a-a_link]: https://a.org

    #### b

    Links to [b][b-b_link].

    [b-b_link]: https://b.org
    """

    assert_code_as_markdown(source, expected)


def test_duplicate_refs_across_methods():
    """Test duplicate references across methods in a class."""
    source = """
    class MyClass:
        def method_a(self):
            \"\"\"First method with [link][1].

            [1]: https://first.com
            \"\"\"
            pass

        def method_b(self):
            \"\"\"Second method with [link][1].

            [1]: https://second.com
            \"\"\"
            pass
    """

    expected = """
    ## MyClass Objects

    ```python
    class MyClass()
    ```

    #### method\\_a

    First method with [link][method_a-1].

    [method_a-1]: https://first.com

    #### method\\_b

    Second method with [link][method_b-1].

    [method_b-1]: https://second.com
    """

    assert_code_as_markdown(source, expected)
