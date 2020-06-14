
from . import assert_processor_result
from pydoc_markdown.contrib.processors.google import GoogleProcessor


def test_google_processor(processor=None):
  assert_processor_result(processor or GoogleProcessor(),
  '''
  Args:
    s (str): A string.
    b (int): An int.
  Returns:
    any: Something funny.
  ''',
  '''
  **Arguments**:

  - `s` _str_ - A string.
  - `b` _int_ - An int.

  **Returns**:

  - `any` - Something funny.
  ''')

  assert_processor_result(processor or GoogleProcessor(),
  '''
  Example:

  ```py
  scanner = ListScanner(lst)
  for value in scanner.safe_iter():
    if some_condition(value):
      value = scanner.advance()
  ```
  ''',
  '''
  **Example**:


  ```py
  scanner = ListScanner(lst)
  for value in scanner.safe_iter():
    if some_condition(value):
      value = scanner.advance()
  ```
  ''')
