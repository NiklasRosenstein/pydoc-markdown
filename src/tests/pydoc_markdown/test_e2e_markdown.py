
from pydoc_markdown import PydocMarkdown
import pytest
import textwrap


def assert_code_as_markdown(source_code, markdown):
  config = PydocMarkdown()
  config.renderer.render_toc = False
  module = config.loaders[0].load_source(textwrap.dedent(source_code),
    '_inline', '<string>')
  [config.graph.add_module(v) for v in module.members.values()]
  config.process()
  result = config.renderer.render_to_string(config.graph)
  assert '\n'.join([x.rstrip() for x in result.strip().split('\n')]) == \
         '\n'.join([x.rstrip() for x in textwrap.dedent(markdown).strip().split('\n')])


def test_preprocessing():
  assert_code_as_markdown(
  '''
  def func(s: str) -> List[str]:
    """ Docstring goes here.

    # Arguments
    s (str): Some string value.

    # Returns
    List[str]: Some more strings. """
  ''',
  '''
  # `func()`

  ```python
  def func(s: str) -> List[str]
  ```

  Docstring goes here.

  __Arguments__

  - __s (str)__: Some string value.

  __Returns__

  `List[str]`: Some more strings.
  ''')


def test_starred_arguments():
  assert_code_as_markdown(
  '''
  def a(*args, **kwargs):
      """Docstring goes here."""
  def b(abc, *,):
      """Docstring goes here."""
  def c(abc, *, defg):
      """Docstring goes here."""
  ''',
  '''
  # `a()`

  ```python
  def a(*args, **kwargs)
  ```

  Docstring goes here.

  # `b()`

  ```python
  def b(abc, *)
  ```

  Docstring goes here.

  # `c()`

  ```python
  def c(abc, *, defg)
  ```

  Docstring goes here.
  ''')
