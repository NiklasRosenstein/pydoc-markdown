
"""
`pydoc_markdown.interfaces`
===========================

This module defines the interfaces that can to be implemented for
Pydoc-Markdown to implement custom loaders for documentation data,
processors or renderers.
"""

from nr.types.structured import Object, extract
from nr.types.interface import Interface, attr, default, staticattr
from .reflection import Module, ModuleGraph
from .utils import load_entry_point


class Configurable(Interface):
  """
  This interface represents an object that provides information on how it can
  be configured via a YAML configuration file.

  Implementations of this class can usually be loaded using the
  [[load_implementation()]] function via the entrypoint specified on the
  implementation class
  """

  ENTRYPOINT_NAME = None  # type: str
  CONFIG_CLASS = None  # type: Type[Object]
  config = attr(default=None)  # type: Optional[Object]

  @staticattr
  @classmethod
  def make_instance(cls, impl_name, config):  # type: (str, Any) -> Configurable
    instance = load_implementation(cls, impl_name)()
    instance.config = extract(config, instance.CONFIG_CLASS)
    return instance


class Loader(Configurable):
  """
  This interface describes an object that is capable of loading documentation
  data. The location from which the documentation is loaded must be defined
  with the configuration class.
  """

  ENTRYPOINT_NAME = 'pydoc_markdown.interfaces.Loader'

  def load(self, config, graph):  # type: (Object, ModuleGraph) -> None
    """
    Fill the [[ModuleGraph]].
    """


class LoaderError(Exception):
  pass


class Processor(Configurable):
  """
  A processor is an object that takes a #ModuleGraph object as an input and
  transforms it in an arbitrary way. This usually processes docstrings to
  convert from various documentation syntaxes to plain Markdown.
  """

  ENTRYPOINT_NAME = 'pydoc_markdown.interfaces.Processor'

  def process(self, config, graph):  # type: (Object, ModuleGraph) -> None
    pass


class Renderer(Processor):
  """
  A renderer is an object that takes a #ModuleGraph as an input and produces
  output files or writes to stdout. It may also expose additional command-line
  arguments. There can only be one renderer at the end of the processor chain.

  Note that sometimes a renderer may need to perform some processing before
  the render step. To keep the possibility open that a renderer may implement
  generic processing that could be used without the actual renderering
  functionality, #Renderer is a subclass of #Processor.
  """

  ENTRYPOINT_NAME = 'pydoc_markdown.interfaces.Renderer'

  @default
  def process(self, config, graph):  # type: (Object, ModuleGraph) -> None
    pass

  def render(self, config, graph):  # type: (Object, ModuleGraph) -> None
    pass


def load_implementation(interface, impl_name):
  """
  Loads an implementation of the specified *interface* (which must be a class
  that provides an `ENTRYPOINT_NAME` attribute) that has the name *impl_name*.
  The loaded class must implement *interface* or else a #RuntimeError is
  raised.
  """

  if not issubclass(interface, Interface):
    raise TypeError('expected Interface subclass')
  if not hasattr(interface, 'ENTRYPOINT_NAME'):
    raise TypeError('interface {} has no attribute ENTRYPOINT_NAME'
      .format(interface.__name__))

  cls = load_entry_point(interface.ENTRYPOINT_NAME, impl_name).load()
  if not interface.implemented_by(cls):
    raise RuntimeError('entrypoint "{}" (group {}) does not implement '
      'the {} interface'.format(impl_name, interface.ENTRYPOINT_NAME,
        interface.__name__))

  return cls
