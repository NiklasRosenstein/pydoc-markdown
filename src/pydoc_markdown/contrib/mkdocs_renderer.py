
"""
Produces MkDocs structure.
"""


from nr.types.structured import Field, Object
from nr.types.interface import implements
from pydoc_markdown.contrib.markdown_rendere import MarkdownRenderer
from pydoc_markdown.interfaces import Renderer


class MkDocsRendererConfig(Object):
  output_directory = Field(str)


@implements(Renderer)
class MkDocsRenderer(object):

  def get_config_class(self):
    return MkDocsRendererConfig

  def render(self, modules):
    for m in modules:
      filename = os.path.join(self.config.output_directory, m.name + '.md')
      print(filename)
