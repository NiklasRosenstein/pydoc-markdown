
import logging
import typing as t
from pathlib import Path

import docspec
from nr.util.plugins import load_entrypoint
from novella.markdown.preprocessor import MarkdownFile, MarkdownFiles, MarkdownPreprocessor
from novella.markdown.tagparser import parse_block_tags, replace_tags, Tag
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.interfaces import Context, Loader, Processor, SinglePageRenderer
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

logger = logging.getLogger(__name__)


class PydocTagPreprocessor(MarkdownPreprocessor):
  """ Implements the `@pydoc` tag for Novella preprocesing. """

  _loader: Loader
  _processors: t.List[Processor]
  _renderer: SinglePageRenderer

  def __init__(self) -> None:
    # Heuristic to provide a sensible default configuration of the plugin.
    if Path.cwd().name.lower() in ('docs', 'documentation'):
      search_path = ['../src', '..']
    else:
      search_path = ['src', '.']

    self._loader = PythonLoader(search_path=search_path)
    self._processors = [FilterProcessor(), SmartProcessor(), CrossrefProcessor()]
    self._renderer = MarkdownRenderer()

  @t.overload
  def loader(self) -> Loader: ...

  @t.overload
  def loader(self, loader: str | Loader, closure: t.Callable[[Loader], t.Any] | None) -> None: ...

  def loader(self, loader=None, closure=None):
    if loader is not None:
      if isinstance(loader, str):
        loader = t.cast(Loader, load_entrypoint('pydoc_markdown.interfaces.Loader', loader)())
      if closure is not None:
        closure(loader)
      self._loader = loader
    else:
      if self._loader is None:
        raise RuntimeError('no loader has been configured yet')
      return self._loader

  @t.overload
  def renderer(self) -> SinglePageRenderer: ...

  @t.overload
  def renderer(self, renderer: str | Loader, closure: t.Callable[[Loader], t.Any] | None) -> None: ...

  def renderer(self, renderer=None, closure=None):
    if renderer is not None:
      if isinstance(renderer, str):
        renderer = load_entrypoint('pydoc_markdown.interfaces.Renderer', renderer)()
        if not isinstance(renderer, SinglePageRenderer):
          raise RuntimeError(f'not a single page renderer: {type(renderer).__name__}')
      if closure is not None:
        closure(renderer)
      self._renderer = renderer
    else:
      return self._renderer

  def process_files(self, files: MarkdownFiles) -> None:
    context = Context(str(Path.cwd()))
    self._loader.init(context)

    modules = list(self._loader.load())
    for processor in self._processors:
      processor.process(modules, None)  # TODO: Add resolver here to render Novella {@link} tags?

    for file in files:
      tags = [t for t in parse_block_tags(file.content) if t.name == 'pydoc']
      file.content = replace_tags(file.content, tags, lambda t: self._replace_tag(modules, file, t))

  def _replace_tag(self, modules: t.List[docspec.Module], file: MarkdownFile, tag: Tag) -> str | None:
    fqn = tag.args.strip()
    objects = get_objects_by_fqn(modules, fqn)
    if len(objects) > 1:
      logger.warning('  found multiple matches for Python FQN <fg=cyan>%s</fg>', fqn)
    elif not objects:
      logger.warning('  found no match for Python FQN <fg=cyan>%s</fg>', fqn)
      return None

    import io
    fp = io.StringIO()
    self._renderer.render_single_page(fp, [objects[0]])  # type: ignore  # TODO (@NiklasRosenstein): New interface to render single API objects?
    return fp.getvalue()


def get_objects_by_fqn(modules: t.Sequence[docspec.Module], fqn: str) -> t.List[docspec.ApiObject]:

  def _match(results: list[docspec.ApiObject]) -> t.Callable[[docspec.ApiObject], t.Any]:
    def matcher(obj: docspec.ApiObject) -> None:
      current_fqn = '.'.join(y.name for y in obj.path)
      if current_fqn == fqn:
        results.append(obj)
    return matcher

  results: list[docspec.ApiObject] = []
  docspec.visit(modules, _match(results))
  return results
