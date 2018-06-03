
def function_without_docstrings(foo):
  pass


def function_with_docstring_on_same_line():
  """This is a pretty cool function.

  # Arguments
  None actually.

  # Example
  ```python
  # This is a very simple example.
  mycoolfunction(samplesize, width, **options)
  ```

  See also: #function_without_docstrings().
  See also: [this page](https://keras.io/layers/convolutional/#conv2d) for
    the list of possible arguments.
  """


def mycoolfunction(samplesize, width=32, **options):
  """
  This is a pretty cool function.

  # Arguments
  samplesize (int): Test sample size.
  width (int): The width.
  options: Additional options

  # Example
  ```python
  # This is a very simple example.
  mycoolfunction(samplesize, width, **options)
  ```

  See also: #myothercoolfunction().
  """

  pass


def myothercoolfunction(prettycool, url):
  """
  Don't you think?

      # This is part of a code block and will not be transformed.
      Code here

  ```
  # This is also part of a code block and will not be transformed.
  More code here
  ```

  # Parameters
  prettycool (any): Some parameter.
  url (string): the url for this thing (default: 'http://localhost#foobar')
  """

  pass

def add(a, b):
  """ Add two numbers.

  # Arguments

  a (int): First number
  b (int): Second number

  # Example

      assert add(2, 3) == 5

  Simple as that.

  Worth checking out: https://en.wikipedia.org/wiki/Addition#Properties
  """

  return a + b


class Breakfast(object):
  """
  This is a very simple class.

  # Arguments

  spam (Spam): 200g of spam
  eggs (Egg): 3 eggs
  ham (Ham): As much ham as you like.
  """

  def __init__(self, spam, eggs, ham=None):
    pass

  def __call__(self):
    """
    This is #Breakfast.__call__().
    """

  def cook(self):
    """
    Cooks the spam.

    # Raises

    OvercookError: If it cooked for too long and burned.
    """

  @property
  def price(self):
    " The price is hot. "
    return 33


b = Breakfast(True, False)


def rest_function(a, b, c):
  """
  This function is documented using ReST Syntax.

  :param a: The first parameter.
  :param b: The second parameter.
  :param c: The third parameter.
  :raise RuntimeError: Maybe sometimes.
  :return: Not much, really.
  """


class ClassWithoutDocs(object):

  def dosomething(self):
    " Abc. "

  @property
  def someprop(self):
    " Some property. "

  @classmethod
  def a_classmethod(self):
    " Test. "

  @staticmethod
  def a_staticmethod():
    pass
