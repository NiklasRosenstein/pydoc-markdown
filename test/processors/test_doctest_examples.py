import pytest
from docstring_parser import DocstringStyle

from pydoc_markdown.contrib.processors.google import GoogleProcessor
from pydoc_markdown.contrib.processors.pydocmd import PydocmdProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor, fence_doctest_blocks

from . import assert_processor_result


@pytest.mark.parametrize("heading", ["Example", "Examples"])
def test_google_doctest_examples(heading: str) -> None:
    assert_processor_result(
        GoogleProcessor(),
        f"""
        Summary.

        {heading}:
            Introductory prose.

            >>> add(
            ...     1,
            ...     2,
            ... )
            3

            Between the blocks.

            >>> greet()
            hello

            Closing prose.
        """,
        f"""
        Summary.

        **{heading}**:

          Introductory prose.

        ```python
        >>> add(
        ...     1,
        ...     2,
        ... )
        3
        ```

          Between the blocks.

        ```python
        >>> greet()
        hello
        ```

          Closing prose.
        """,
    )


def test_numpy_doctest_examples() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.NUMPYDOC),
        """
        Summary.

        Examples
        --------
        Introductory prose.

        >>> add(
        ...     1,
        ...     2,
        ... )
        3

        Between the blocks.

        >>> greet()
        hello

        Closing prose.
        """,
        """
        Summary.

        **Examples**:

        Introductory prose.

        ```python
        >>> add(
        ...     1,
        ...     2,
        ... )
        3
        ```

        Between the blocks.

        ```python
        >>> greet()
        hello
        ```

        Closing prose.
        """,
    )


def test_google_doctest_examples_preserve_dictionary_output() -> None:
    assert_processor_result(
        GoogleProcessor(),
        """
        Examples:
            >>> {"answer": 42}
            {'answer': 42}
        """,
        """
        **Examples**:

        ```python
        >>> {"answer": 42}
        {'answer': 42}
        ```
        """,
    )


def test_doctest_blocks_can_be_disabled() -> None:
    assert_processor_result(
        GoogleProcessor(render_doctest_blocks=False),
        """
        Examples:
            >>> add(1, 2)
            3
        """,
        """
        **Examples**:

          >>> add(1, 2)
          3
        """,
    )


def test_doctest_text_outside_examples_is_rewritten() -> None:
    assert_processor_result(
        GoogleProcessor(),
        """
        >>> outside_examples()
        prose mentioning >>> is not a prompt

        Notes:
            >>> also_outside_examples()
        Examples:
            prose mentioning >>> is still not a prompt
        """,
        """
        ```python
        >>> outside_examples()
        prose mentioning >>> is not a prompt
        ```

        **Notes**:

        ```python
        >>> also_outside_examples()
        ```

        **Examples**:

          prose mentioning >>> is still not a prompt
        """,
    )


def test_existing_fence_inside_examples_is_not_rewritten() -> None:
    assert_processor_result(
        GoogleProcessor(),
        """
        Examples:
            ```text
            >>> already_fenced()
            ```
        """,
        """
        **Examples**:

            ```text
            >>> already_fenced()
            ```
        """,
    )


def test_existing_tilde_fence_inside_examples_is_not_rewritten() -> None:
    assert_processor_result(
        GoogleProcessor(),
        """
        Examples:
            ~~~python
            >>> already_fenced()
            ~~~
        """,
        """
        **Examples**:

            ~~~python
            >>> already_fenced()
            ~~~
        """,
    )


def test_longer_fence_is_not_closed_by_shorter_fence_inside_it() -> None:
    assert_processor_result(
        GoogleProcessor(),
        """
        Examples:
            ````text
            ```
            >>> already_fenced()
            ```
            ````
        """,
        """
        **Examples**:

            ````text
            ```
            >>> already_fenced()
            ```
            ````
        """,
    )


def test_generated_fence_does_not_collide_with_doctest_output() -> None:
    assert_processor_result(
        GoogleProcessor(),
        """
        Examples:
            >>> print("```")
            ```
        """,
        """
        **Examples**:

        ````python
        >>> print("```")
        ```
        ````
        """,
    )


def test_pydocmd_tracks_collision_safe_fence_delimiter() -> None:
    assert_processor_result(
        PydocmdProcessor(),
        '>>> print("```")\n```\n\n# Arguments\noutside: value',
        '````python\n>>> print("```")\n```\n````\n\n__Arguments__\n\n- __outside__: value',
    )


def test_google_recognizes_generated_fence_nested_in_list() -> None:
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    - Case:\n        >>> example()\n        item: value",
        "**Examples**:\n\n  - Case:\n        ```python\n        >>> example()\n        item: value\n        ```",
    )


def test_generated_fence_preserves_list_container_indentation() -> None:
    assert fence_doctest_blocks("- First:\n\n    >>> example()\n    result") == (
        "- First:\n\n    ```python\n    >>> example()\n    result\n    ```"
    )


def test_generated_fence_finds_list_container_before_introductory_prose() -> None:
    assert fence_doctest_blocks("- Item:\n\n    Intro.\n\n    >>> example()\n    result") == (
        "- Item:\n\n    Intro.\n\n    ```python\n    >>> example()\n    result\n    ```"
    )


def test_smart_processor_fences_plain_docstring_doctests() -> None:
    assert_processor_result(
        SmartProcessor(),
        "Plain docstring.\n\n>>> example()\nresult",
        "Plain docstring.\n\n```python\n>>> example()\nresult\n```",
    )


@pytest.mark.parametrize("processor", [PydocmdProcessor(), SmartProcessor()])
def test_pydocmd_fences_doctests_before_rewriting_section_syntax(processor) -> None:
    assert_processor_result(
        processor,
        ">>> example()\n# Arguments\nitem: value\n\n# Arguments\noutside: value",
        ("```python\n>>> example()\n# Arguments\nitem: value\n```\n\n__Arguments__\n\n- __outside__: value"),
    )


def test_sphinx_processor_protects_field_looking_doctest_output() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.REST),
        'Example:\n\n    >>> print(":return: value")\n    :return: value\n\n:param item: An item.',
        (
            'Example:\n\n```python\n>>> print(":return: value")\n:return: value\n```\n\n'
            "**Arguments**:\n\n- `item`: An item."
        ),
    )


def test_sphinx_doctest_placeholder_does_not_collide_with_content() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.REST),
        "__PYDOC_MARKDOWN_DOCTEST_BLOCK_0__\n\n>>> example()\nresult",
        "__PYDOC_MARKDOWN_DOCTEST_BLOCK_0__\n\n```python\n>>> example()\nresult\n```",
    )


def test_sphinx_doctest_placeholders_do_not_reuse_allocated_tokens() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.REST),
        "__PYDOC_MARKDOWN_DOCTEST_BLOCK_0__\n\n>>> first()\none\n\n>>> second()\ntwo",
        ("__PYDOC_MARKDOWN_DOCTEST_BLOCK_0__\n\n```python\n>>> first()\none\n```\n\n```python\n>>> second()\ntwo\n```"),
    )


def test_sphinx_processor_restores_doctest_field_description_as_nested_block() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.REST),
        ":param item:\n    >>> example()\n    result",
        "**Arguments**:\n\n- `item`:\n\n  ```python\n  >>> example()\n  result\n  ```",
    )


def test_sphinx_processor_nests_doctest_after_field_description_prose() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.REST),
        ":param item: Intro.\n\n    >>> example()\n    result",
        "**Arguments**:\n\n- `item`: Intro.\n\n  ```python\n  >>> example()\n  result\n  ```",
    )


def test_sphinx_processor_nests_multiple_doctests_in_field_description() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.REST),
        ":param item:\n    >>> first()\n    one\n\n    >>> second()\n    two",
        (
            "**Arguments**:\n\n- `item`:\n\n  ```python\n  >>> first()\n  one\n  ```\n\n"
            "  ```python\n  >>> second()\n  two\n  ```"
        ),
    )


def test_sphinx_processor_restores_blockquoted_doctest_without_duplicate_prefix() -> None:
    assert_processor_result(
        SphinxProcessor(style=DocstringStyle.REST),
        "> >>> example()\n> result",
        "> ```python\n> >>> example()\n> result\n> ```",
    )


def test_top_level_indented_code_does_not_hide_later_doctest() -> None:
    assert fence_doctest_blocks("    ```literal\n\n>>> example()\nresult") == (
        "    ```literal\n\n```python\n>>> example()\nresult\n```"
    )


def test_fence_state_ends_with_its_blockquote_container() -> None:
    text = "> ```text\n> quoted content\n```text\n>>> already_fenced()\n```"
    assert fence_doctest_blocks(text) == text


def test_fence_state_ends_with_its_list_container() -> None:
    text = "- Item:\n\n    ```text\n    list content\n```text\n>>> already_fenced()\n```"
    assert fence_doctest_blocks(text) == text


def test_fence_indented_inside_list_remains_protected() -> None:
    text = "- Item:\n\n    ```text\n    >>> already_fenced()\n    ```"
    assert fence_doctest_blocks(text) == text


def test_indented_backticks_do_not_close_top_level_fence() -> None:
    text = "```text\n    ```\n>>> already_fenced()\n```"
    assert fence_doctest_blocks(text) == text


def test_closer_indentation_is_relative_to_fence_container() -> None:
    text = "   ```text\n    ```\n   >>> already_fenced()\n   ```"
    assert fence_doctest_blocks(text) == text


def test_generated_fence_preserves_blockquote_prefixes() -> None:
    assert fence_doctest_blocks("> >>> example()\n> result") == ("> ```python\n> >>> example()\n> result\n> ```")


def test_google_doctest_detects_blockquote_after_section_indent() -> None:
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    > >>> example()\n    > result",
        "**Examples**:\n\n  > ```python\n  > >>> example()\n  > result\n  > ```",
    )


def test_pydocmd_fence_state_ends_with_container() -> None:
    text = "- Item:\n    ```text\n    content\n```text\n# Arguments\ninside: value\n```"
    assert_processor_result(PydocmdProcessor(), text, text)
