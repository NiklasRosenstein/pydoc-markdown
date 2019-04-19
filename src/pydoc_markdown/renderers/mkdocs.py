
"""
Produces MkDocs structure.
"""

from . import Renderer
from .markdown import MarkdownRenderer
from nr.config import Partial


class MkDocsRendererConfig(Partial):
  __fields__ = [
    ('output_directory', str),
  ]


class MkDocsRenderer(Renderer):

  config_class = MkDocsRendererConfig

  def render(self, modules):
    for m in modules:
      filename = os.path.join(self.config.output_directory, m.name + '.md')
      print(filename)


renderer_class = MkDocsRenderer
