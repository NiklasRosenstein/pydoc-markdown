import pytest

from pydoc_markdown.util.misc import escape_curly_brackets, escape_except_blockquotes


def test__escape_except_blockquotes() -> None:
    assert escape_except_blockquotes(
        """
        1 < 2?

        ```
        Yes, 1 < 2.
        ```
        """
    ) == (
        """
        1 &lt; 2?

        ```
        Yes, 1 < 2.
        ```
        """
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("Hello {world}", "Hello \\{world\\}", id="plain-text"),
        pytest.param("Use `{x}` and ``{y} `z` ``", "Use `{x}` and ``{y} `z` ``", id="inline-code"),
        pytest.param("```python\nf'{x}'\n```\n{y}", "```python\nf'{x}'\n```\n\\{y\\}", id="backtick-fence"),
        pytest.param("~~~\n{x}\n~~~\n{y}", "~~~\n{x}\n~~~\n\\{y\\}", id="tilde-fence"),
        pytest.param("Already \\{escaped\\}", "Already \\{escaped\\}", id="already-escaped"),
    ],
)
def test__escape_curly_brackets(text: str, expected: str) -> None:
    assert escape_curly_brackets(text) == expected
