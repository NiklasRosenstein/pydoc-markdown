
from .test_utils import assert_text_equals
from docspec_python import parse_python_module, ParserOptions
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.processors.filter import FilterProcessor
import io
import textwrap


def assert_code_as_markdown(source_code, markdown, full=False, parser_options=None, renderer_options=None):
  config = PydocMarkdown()

  # Init the settings in which we want to run the tests.
  config.renderer.insert_header_anchors = False
  config.renderer.add_member_class_prefix = False
  config.renderer.render_toc = False
  config.renderer.render_module_header = full
  for key, value in (renderer_options or {}).items():
    assert hasattr(config.renderer, key), key
    setattr(config.renderer, key, value)
  filter_processor = next(x for x in config.processors if isinstance(x, FilterProcessor))
  filter_processor.documented_only = False

  # Load the source code as a module.
  modules = [parse_python_module(
    io.StringIO(textwrap.dedent(source_code)),
    filename='<string>',
    module_name='_inline',
    options=parser_options,
  )]

  config.process(modules)
  result = config.renderer.render_to_string(modules)
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
  #### func

  ```python
  func(s: str) -> List[str]
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
  #### a

  ```python
  a(*args, **kwargs)
  ```

  Docstring goes here.

  #### b

  ```python
  b(abc)
  ```

  Docstring goes here.

  #### c

  ```python
  c(abc, *, defg)
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
  ## MyError Objects

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
  ## Foo Objects

  ```python
  class Foo()
  ```

  This is not a member docstring.

  #### member
  ''',
  parser_options=ParserOptions(treat_singleline_comment_blocks_as_docstrings=True))

  assert_code_as_markdown(
  '''
  class Class:
    """
    The class documentation!
    """

    def __init__(self, param):
      """
      The constructor.

      :param param: A parameter.
      """
      self.param = param
  ''',
  '''
  ## Class Objects

  ```python
  class Class()
  ```

  The class documentation!

  #### \\_\\_init\\_\\_

  ```python
   | __init__(param)
  ```

  The constructor.

  **Arguments**:

  - `param`: A parameter.
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
  ## PetType Objects

  ```python
  class PetType(enum.Enum)
  ```

  Enumeration to identify possible pet types.

  #### DOG

  #### CAT

  #### MOUSE
  ''')


def test_module_docstring():
  assert_code_as_markdown(
  '''
  # This is the module docstring.
  ''',
  '''
  # \\_inline

  This is the module docstring.
  ''',
  full=True,
  parser_options=ParserOptions(treat_singleline_comment_blocks_as_docstrings=True))


  assert_code_as_markdown(
  '''
  # LICENSE INFO HERE.

  """ This is the module docstring. """

  ''',
  '''
  # \\_inline

  This is the module docstring.
  ''',
  full=True)


def test_attribute_docstring():
  assert_code_as_markdown(
  '''
  class Foo:
    #: This is a member docstring.
    member = None

    #: This is a member with a type hint.
    int_member: int = 32

    #: A member with type hint but no value.
    float_member: float
  ''',
  '''
  ## Foo Objects

  ```python
  class Foo()
  ```

  #### member

  This is a member docstring.

  #### int\\_member

  This is a member with a type hint.

  #### float\\_member

  A member with type hint but no value.
  ''')

  assert_code_as_markdown(
  '''
  class Foo:
    member = None
    """ This is a member docstring. """
  ''',
  '''
  ## Foo Objects

  ```python
  class Foo()
  ```

  #### member

  This is a member docstring.
  ''')


def test_constants():
  assert_code_as_markdown(
  '''
  class Dummy:
    #: Magic number
    a = 42
  ''',
  '''
  ## Dummy Objects

  ```python
  class Dummy()
  ```

  #### a

  ```python
  a = 42
  ```

  Magic number
  ''',
  renderer_options={'data_code_block': True})
