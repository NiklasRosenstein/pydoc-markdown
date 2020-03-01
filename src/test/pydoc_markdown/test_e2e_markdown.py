
from pydoc_markdown import PydocMarkdown
from test.pydoc_markdown.utils import assert_text_equals
import textwrap


def assert_code_as_markdown(source_code, markdown, full=False):
  config = PydocMarkdown()
  config.renderer.insert_heading_anchors = False
  config.renderer.render_toc = False
  module = config.loaders[0].load_source(textwrap.dedent(source_code),
    '_inline', '<string>')
  if full:
    config.graph.add_module(module)
  else:
    for member in module.members.values():
      config.graph.add_module(member)
  config.process()
  result = config.renderer.render_to_string(config.graph)
  assert_text_equals(result, textwrap.dedent(markdown))


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

  - __s__ (`str`): Some string value.

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


def test_class():
  # https://github.com/NiklasRosenstein/pydoc-markdown/issues/83
  assert_code_as_markdown(
  '''
  class MyError(RuntimeError):
    """ Error raised when my thing happens. """
    pass
  ''',
  '''
  # `MyError` Objects

  ```python
  class MyError(RuntimeError)
  ```

  Error raised when my thing happens.
  ''')

  assert_code_as_markdown(
  '''
  class Foo:
    # This is not a member docstring.
    member = None
  ''',
  '''
  # `Foo` Objects

  ```python
  class Foo()
  ```

  This is not a member docstring.

  ## `member`
  ''')


def test_enum():
  assert_code_as_markdown(
  '''
    class PetType(enum.Enum):
      """ Enumeration to identify possible pet types. """
      DOG = 0
      CAT = 1
      MOUSE = 2  #: Mice are rare.
  ''',
  '''
  # `PetType` Objects

  ```python
  class PetType(enum.Enum)
  ```

  Enumeration to identify possible pet types.

  ## `DOG`

  ## `CAT`

  ## `MOUSE`
  ''')


def test_module_docstring():
  assert_code_as_markdown(
  '''
  # This is the module docstring.
  ''',
  '''
  # `_inline`

  This is the module docstring.
  ''',
  full=True)


  assert_code_as_markdown(
  '''
  # LICENSE INFO HERE.

  """ This is the module docstring. """

  ''',
  '''
  # `_inline`

  This is the module docstring.
  ''',
  full=True)


def test_attribute_docstring():
  assert_code_as_markdown(
  '''
  class Foo:
    #: This is a member docstring.
    member = None
  ''',
  '''
  # `Foo` Objects

  ```python
  class Foo()
  ```

  ## `member`

  This is a member docstring.
  ''')

  assert_code_as_markdown(
  '''
  class Foo:
    member = None
    """ This is a member docstring. """
  ''',
  '''
  # `Foo` Objects

  ```python
  class Foo()
  ```

  ## `member`

  This is a member docstring.
  ''')
