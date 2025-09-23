from pydoc_markdown.util.misc import escape_except_blockquotes, escape_curly_brackets


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


def test__escape_curly_brackets() -> None:
    # Test basic escaping
    assert escape_curly_brackets("Hello {world}") == "Hello \\{world\\}"
    
    # Test escaping with inline code - curly brackets should NOT be escaped inside backticks
    assert escape_curly_brackets("Use `{variable}` in your code") == "Use `{variable}` in your code"
    
    # Test escaping with code blocks - curly brackets should NOT be escaped inside triple backticks
    code_block_input = """Here is an example:

```python
def format_string():
    return f"Hello {name}!"
```

But outside code blocks, \\{these\\} should be escaped."""
    
    expected_output = """Here is an example:

```python
def format_string():
    return f"Hello {name}!"
```

But outside code blocks, \\\\\\{these\\\\\\} should be escaped."""
    
    assert escape_curly_brackets(code_block_input) == expected_output
    
    # Test mixed case with both inline code and regular text
    mixed_input = "Regular {bracket} and `code {bracket}` and more {regular}"
    expected_mixed = "Regular \\{bracket\\} and `code {bracket}` and more \\{regular\\}"
    assert escape_curly_brackets(mixed_input) == expected_mixed
    
    # Test multiple code blocks
    multi_code_input = """First `{inline}` and then:
```
{block_code}
```
And {regular} text."""
    
    expected_multi = """First `{inline}` and then:
```
{block_code}
```
And \\{regular\\} text."""
    
    assert escape_curly_brackets(multi_code_input) == expected_multi
