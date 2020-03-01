
from . import assert_processor_result
from pydoc_markdown.contrib.processors.pydocmd import PydocmdProcessor


def test_pydocmd_processor(processor=None):
  assert_processor_result(processor or PydocmdProcessor(),
  '''
  # Arguments
  s (str): A string.
  b (int): An int.
  ''',
  '''
  __Arguments__

  - __s__ (`str`): A string.
  - __b__ (`int`): An int.
  ''')

  # Intentionally not using the supplied processor as this is caught by
  # the Google processor.
  assert_processor_result(PydocmdProcessor(),
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
  Example:

  ```py
  scanner = ListScanner(lst)
  for value in scanner.safe_iter():
    if some_condition(value):
      value = scanner.advance()
  ```
  ''')
