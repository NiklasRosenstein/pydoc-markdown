from pydoc_markdown.util.misc import escape_except_blockquotes


def test__escape_except_blockquotes() -> None:
    assert (
        escape_except_blockquotes(
            """
        1 < 2?

        ```
        Yes, 1 < 2.
        ```
        """
        )
        == (
            """
        1 &lt; 2?

        ```
        Yes, 1 < 2.
        ```
        """
        )
    )
