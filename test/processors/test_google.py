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


def test_google_processor_preserves_tab_indented_nested_lists():
    assert_processor_result(
        GoogleProcessor(),
        "Args:\n\titems: A nested list.\n\t\t- Test\n\t\t\t- nested",
        "**Arguments**:\n\n- `items` - A nested list.\n  - Test\n      - nested",
    )


def test_google_processor_rebases_mixed_indentation_by_markdown_columns():
    assert_processor_result(
        GoogleProcessor(),
        "Args:\n    items: A nested list.\n\t\t- Test\n\t    \t- nested",
        "**Arguments**:\n\n- `items` - A nested list.\n  - Test\n      - nested",
    )


def test_google_processor_rebases_mixed_indentation_in_example_fences():
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n\tHow to use:\n    ```python\n\tif True:\n    \tprint('yes')\n\t```",
        "**Examples**:\n\n  How to use:\n```python\nif True:\n    print('yes')\n```",
    )


def test_google_processor_preserves_nested_example_fence_indentation():
    assert_processor_result(
        GoogleProcessor(),
        ("Examples:\n    - With code:\n        ```python\n        if True:\n            print('yes')\n        ```"),
        ("**Examples**:\n\n  - With code:\n    ```python\n    if True:\n        print('yes')\n    ```"),
    )


def test_google_processor_uses_minimum_section_indentation():
    assert_processor_result(
        GoogleProcessor(),
        "Notes:\n        Extra-indented first line.\n    Section baseline.",
        "**Notes**:\n\n      Extra-indented first line.\n  Section baseline.",
    )


def test_google_processor_rebases_fences_outside_examples():
    assert_processor_result(
        GoogleProcessor(),
        "Notes:\n    ```python\n    print('yes')\n    ```",
        "**Notes**:\n\n```python\nprint('yes')\n```",
    )


def test_google_processor_rebases_tilde_fences_in_examples():
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    ~~~python\n    print('yes')\n    ~~~",
        "**Examples**:\n\n~~~python\nprint('yes')\n~~~",
    )


def test_google_processor_preserves_two_space_list_fence_nesting():
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    - With code:\n      ```python\n      print('yes')\n      ```",
        "**Examples**:\n\n  - With code:\n    ```python\n    print('yes')\n    ```",
    )


def test_google_processor_tracks_list_nesting_across_prose():
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    - With code:\n      Description.\n      ```python\n      print('yes')\n      ```",
        "**Examples**:\n\n  - With code:\n    Description.\n    ```python\n    print('yes')\n    ```",
    )


def test_google_processor_preserves_preamble_order_around_tilde_fences():
    assert_processor_result(
        GoogleProcessor(),
        "~~~python\nprint('before')\n~~~\nAfter the fence.\nArgs:\n    value: A value.",
        "~~~python\nprint('before')\n~~~\nAfter the fence.\n\n**Arguments**:\n\n- `value` - A value.",
    )


def test_google_processor_indents_fences_to_ordered_list_content():
    assert_processor_result(
        GoogleProcessor(),
        (
            "Examples:\n"
            "    1. One digit:\n"
            "       ```python\n"
            "       print('one')\n"
            "       ```\n"
            "    10. Two digits:\n"
            "        ```python\n"
            "        print('ten')\n"
            "        ```"
        ),
        (
            "**Examples**:\n\n"
            "  1. One digit:\n"
            "     ```python\n"
            "     print('one')\n"
            "     ```\n"
            "  10. Two digits:\n"
            "      ```python\n"
            "      print('ten')\n"
            "      ```"
        ),
    )


def test_google_processor_rebases_blockquoted_example_fences():
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    > ```python\n    > print('quoted')\n    > ```",
        "**Examples**:\n\n  > ```python\n  > print('quoted')\n  > ```",
    )


def test_google_processor_accounts_for_empty_list_marker_separator():
    assert_processor_result(
        GoogleProcessor(),
        (
            "Examples:\n"
            "    -\n"
            "      ```python\n"
            "      print('bullet')\n"
            "      ```\n"
            "    1.\n"
            "       ```python\n"
            "       print('ordered')\n"
            "       ```"
        ),
        (
            "**Examples**:\n\n"
            "  -\n"
            "    ```python\n"
            "    print('bullet')\n"
            "    ```\n"
            "  1.\n"
            "     ```python\n"
            "     print('ordered')\n"
            "     ```"
        ),
    )


def test_google_processor_does_not_close_top_level_fence_with_quoted_delimiter():
    assert_processor_result(
        GoogleProcessor(),
        ("Examples:\n    ```text\n    > ```\n    still fenced\n    ```\nReturns:\n    str: Done."),
        ("**Examples**:\n\n```text\n> ```\nstill fenced\n```\n\n**Returns**:\n\n- `str` - Done."),
    )


def test_google_processor_keeps_blockquoted_fence_sibling_to_list():
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    - Plain item\n    > ```python\n    > print('quoted')\n    > ```",
        "**Examples**:\n\n  - Plain item\n  > ```python\n  > print('quoted')\n  > ```",
    )


def test_google_processor_preserves_admonition_fence_nesting():
    assert_processor_result(
        GoogleProcessor(),
        "Examples:\n    !!! note\n        ```python\n        print('nested')\n        ```",
        "**Examples**:\n\n  !!! note\n      ```python\n      print('nested')\n      ```",
    )
