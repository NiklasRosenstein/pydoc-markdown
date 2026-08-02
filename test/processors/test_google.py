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
