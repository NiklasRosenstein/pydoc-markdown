
from ..utils import load_entry_point, Configurable

ENTRYPOINT_GROUP_NAME = 'pydoc_markdown.renderers'


class Renderer(Configurable):

  options = []

  def render(self, modules):
    """
    Called to render the API documentation from a list of
    #..parse.reflection.Module objects.
    """

    raise NotImplementedError


def load_renderer(name):
    return load_entry_point(ENTRYPOINT_GROUP_NAME, name).load()
