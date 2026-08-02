import pytest
from docstring_parser import DocstringStyle

from pydoc_markdown.contrib.processors.google import GoogleProcessor
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor

from . import assert_processor_result


@pytest.mark.parametrize("heading", ["Example", "Examples"])
def test_google_doctest_examples(heading: str) -> None:
    assert_processor_result(
        GoogleProcessor(render_doctest_examples=True),
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
        SphinxProcessor(style=DocstringStyle.NUMPYDOC, render_doctest_examples=True),
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
        GoogleProcessor(render_doctest_examples=True),
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


def test_doctest_examples_are_disabled_by_default() -> None:
    assert_processor_result(
        GoogleProcessor(),
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


def test_doctest_text_outside_examples_is_not_rewritten() -> None:
    assert_processor_result(
        GoogleProcessor(render_doctest_examples=True),
        """
        >>> outside_examples()
        prose mentioning >>> is not a prompt

        Notes:
            >>> also_outside_examples()
        Examples:
            prose mentioning >>> is still not a prompt
        """,
        """
        >>> outside_examples()
        prose mentioning >>> is not a prompt

        **Notes**:

          >>> also_outside_examples()

        **Examples**:

        prose mentioning >>> is still not a prompt
        """,
    )


def test_existing_fence_inside_examples_is_not_rewritten() -> None:
    assert_processor_result(
        GoogleProcessor(render_doctest_examples=True),
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
        GoogleProcessor(render_doctest_examples=True),
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
        GoogleProcessor(render_doctest_examples=True),
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
