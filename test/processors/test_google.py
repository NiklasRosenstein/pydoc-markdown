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
