
from pydoc_markdown import PydocMarkdown
import pytest
import textwrap


def assert_code_as_markdown(source_code, markdown):
  config = PydocMarkdown()
  config.renderer.render_toc = False
  module = config.loaders[0].load_source(textwrap.dedent(source_code),
    '_inline', '<string>')
  config.graph.add_module(module)
  config.process()
  result = config.renderer.render_to_string(config.graph)
  assert [x.rstrip() for x in result.strip().split('\n')] == \
         [x.rstrip() for x in textwrap.dedent(markdown).strip().split('\n')]


def test_something():
  assert_code_as_markdown(
  '''
  def test():
    pass
  ''',
  '''
  # `_inline`


  ## `test()`

  ```python
  def test()
  ```
  ''')
