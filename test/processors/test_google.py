import pytest

from pydoc_markdown.contrib.processors.google import GoogleProcessor

from . import assert_processor_result


def test_google_processor(processor=None):
    assert_processor_result(
        processor or GoogleProcessor(),
        """
  Args:
    s (str): A string.
    b (int): An int.
  Returns:
    any: Something funny.
  """,
        """
  **Arguments**:

  - `s` _str_ - A string.
  - `b` _int_ - An int.

  **Returns**:

  - `any` - Something funny.
  """,
    )

    assert_processor_result(
        processor or GoogleProcessor(),
        """
  Args:
    s (str): A string.
              And the description
              takes
              multiple lines.
    b (int): An int.
  Returns:
    any: Something funny.
  """,
        """
  **Arguments**:

  - `s` _str_ - A string.
    And the description
    takes
    multiple lines.
  - `b` _int_ - An int.

  **Returns**:

  - `any` - Something funny.
  """,
    )

    assert_processor_result(
        processor or GoogleProcessor(),
        """
  Example:

  ```py
  scanner = ListScanner(lst)
  for value in scanner.safe_iter():
    if some_condition(value):
      value = scanner.advance()
  ```
  """,
        """
  **Example**:


  ```py
  scanner = ListScanner(lst)
  for value in scanner.safe_iter():
    if some_condition(value):
      value = scanner.advance()
  ```
  """,
    )

    assert_processor_result(
        processor or GoogleProcessor(),
        """
  Args:
    s (str): A string.
    b (int): An int.
  Examples:
    ```
    print("Hello World")
    ```
  Returns:
    any: Something funny.
  """,
        """
  **Arguments**:

  - `s` _str_ - A string.
  - `b` _int_ - An int.

  **Examples**:

  ```
  print("Hello World")
  ```
  
  **Returns**:

  - `any` - Something funny.
  """,
    )

    # Regression test for https://github.com/NiklasRosenstein/pydoc-markdown/issues/182.
    assert_processor_result(
        processor or GoogleProcessor(),
        """
  Examples:

      analysis_instance = make_analysis(DATA_PATH,
                              ["first.c3d", "second.c3d"],
  """,
        """
  **Examples**:


      analysis_instance = make_analysis(DATA_PATH,
                              ["first.c3d", "second.c3d"],
  """,
    )

    # Regression test for https://github.com/NiklasRosenstein/pydoc-markdown/issues/296.
    assert_processor_result(
        processor or GoogleProcessor(),
        """
  Examples:

      How to use:

      ```python
      # A comment
      if True:
          print("Hello")
      ```
  """,
        """
  **Examples**:


    How to use:

  ```python
  # A comment
  if True:
      print("Hello")
  ```
  """,
    )

    # Regression test for https://github.com/NiklasRosenstein/pydoc-markdown/issues/320.
    assert_processor_result(
        processor or GoogleProcessor(),
        """
  Args:
    items: A nested list.
      - Test
        - nested
  """,
        """
  **Arguments**:

  - `items` - A nested list.
    - Test
      - nested
  """,
    )


@pytest.mark.parametrize(
    ("docstring", "expected"),
    [
        pytest.param(
            "Args:\n    items: A nested list.\n\t\t- Test\n\t    \t- nested",
            "**Arguments**:\n\n- `items` - A nested list.\n  - Test\n      - nested",
            id="mixed-tab-and-space-indentation",
        ),
        pytest.param(
            "Notes:\n        Extra-indented first line.\n    Section baseline.",
            "**Notes**:\n\n      Extra-indented first line.\n  Section baseline.",
            id="relative-indentation-from-minimum-section-indent",
        ),
        pytest.param(
            "Notes:\n    ```python\n    print('yes')\n    ```",
            "**Notes**:\n\n```python\nprint('yes')\n```",
            id="fence-outside-examples",
        ),
        pytest.param(
            "Examples:\n    ~~~python\n    print('yes')\n    ~~~",
            "**Examples**:\n\n~~~python\nprint('yes')\n~~~",
            id="tilde-fence",
        ),
        pytest.param(
            "Examples:\n    - With code:\n        ```python\n        if True:\n            print('yes')\n        ```",
            "**Examples**:\n\n  - With code:\n    ```python\n    if True:\n        print('yes')\n    ```",
            id="fence-nested-in-list-item",
        ),
        pytest.param(
            "Examples:\n    10. Two digits:\n        ```python\n        print('ten')\n        ```",
            "**Examples**:\n\n  10. Two digits:\n      ```python\n      print('ten')\n      ```",
            id="fence-nested-in-ordered-list-item",
        ),
        pytest.param(
            "Examples:\n    !!! note\n        ```python\n        print('nested')\n        ```",
            "**Examples**:\n\n  !!! note\n      ```python\n      print('nested')\n      ```",
            id="fence-nested-in-admonition",
        ),
        pytest.param(
            "Examples:\n    ```text\n    > ```\n    still fenced\n    ```\nReturns:\n    str: Done.",
            "**Examples**:\n\n```text\n> ```\nstill fenced\n```\n\n**Returns**:\n\n- `str` - Done.",
            id="quoted-delimiter-does-not-close-fence",
        ),
        pytest.param(
            "Summary.\n\n~~~text\nArgs:\n    x: not a parameter\n~~~\nArgs:\n    value: A value.",
            "Summary.\n\n~~~text\nArgs:\n    x: not a parameter\n~~~\n\n**Arguments**:\n\n- `value` - A value.",
            id="section-keyword-inside-fence-is-literal",
        ),
        pytest.param(
            "Example:\n    Call it like so:\n\n        >>> foo()\n        42",
            "**Example**:\n\n  Call it like so:\n  \n      >>> foo()\n      42",
            id="example-prose-before-nested-literal-block",
        ),
    ],
)
def test_google_processor_indentation(docstring: str, expected: str) -> None:
    assert_processor_result(GoogleProcessor(), docstring, expected)
