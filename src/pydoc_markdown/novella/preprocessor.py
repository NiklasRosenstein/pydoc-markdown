
from __future__ import annotations

import logging
import re
import typing as t
from pathlib import Path

from nr.util.functional import assure
from nr.util.plugins import load_entrypoint
from novella.markdown.preprocessor import MarkdownFile, MarkdownFiles, MarkdownPreprocessor
from novella.markdown.tagparser import parse_block_tags, parse_inline_tags, replace_tags, Tag
from novella.repository import RepositoryType, detect_repository
from pydoc_markdown.contrib.source_linkers import git as git_source_linkers
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.interfaces import Context, Loader, Processor, SingleObjectRenderer, SourceLinker
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer, MarkdownReferenceResolver
from pydoc_markdown.util.docspec import ApiSuite

logger = logging.getLogger(__name__)


def autodetect_source_linker() -> t.Optional[SourceLinker]:
  repo = detect_repository(Path.cwd())
  if not repo or repo.type != RepositoryType.GIT:
    return None

  if 'github.com' in repo.url:
    name = assure(re.search(r'github.com/([^/]+/[^/]+)', repo.url)).group(1)
    return git_source_linkers.GithubSourceLinker(root=repo.root, repo=name, use_branch=True)
  elif 'gitlab.com' in repo.url:
    name = assure(re.search(r'gitlab.com/(.*)', repo.url)).group(1)
    return git_source_linkers.GitlabSourceLinker(root=repo.root, repo=name, use_branch=True)
  elif 'gitea.com' in repo.url:
    name = assure(re.search(r'gitea.com/([^/]+/[^/]+)', repo.url)).group(1)
    return git_source_linkers.GiteaSourceLinker(root=repo.root, repo=name, use_branch=True)

  # TODO (@NiklasRosenstein): BitBucket
  return None


class PydocTagPreprocessor(MarkdownPreprocessor):
  """ Implements the `@pydoc` and `@pylink` tag when using Novella for Markdown preprocessing

  This preprocessor precedes the Novella built-in "anchor" preprocessor as it generates `@anchor` and `{@link}` tags.
  """

  _loader: Loader
  _processors: t.List[Processor]
  _renderer: SingleObjectRenderer
  _suite: ApiSuite | None = None

  def __post_init__(self) -> None:
    # Heuristic to provide a sensible default configuration of the plugin.
    if Path.cwd().name.lower() in ('docs', 'documentation'):
      search_path = ['../src', '..']
    else:
      search_path = ['src', '.']

    source_linker = autodetect_source_linker()
    self._loader = PythonLoader(search_path=search_path)
    self._processors = [
      FilterProcessor(),
      SmartProcessor(),
      # We return the entire link formatted as a Novella {@link} tag in #resolve_ref().
      CrossrefProcessor(resolver_v2=MarkdownReferenceResolver(global_=True)),
    ]
    self._renderer = MarkdownRenderer(
      source_linker=source_linker,
      render_novella_anchors=True,
      render_module_header=False,
      descriptive_class_title='Class ',
    )

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
  def renderer(self) -> SingleObjectRenderer: ...

  @t.overload
  def renderer(self, renderer: str | Loader, closure: t.Callable[[Loader], t.Any] | None) -> None: ...

  def renderer(self, renderer=None, closure=None):
    if renderer is not None:
      if isinstance(renderer, str):
        renderer = load_entrypoint('pydoc_markdown.interfaces.Renderer', renderer)()
        if not isinstance(renderer, SingleObjectRenderer):
          raise RuntimeError(f'not a SingleObjectRenderer: {type(renderer).__name__}')
      if closure is not None:
        closure(renderer)
      self._renderer = renderer
    else:
      return self._renderer

  # MarkdownPreprocessor

  def setup(self) -> None:
    if self.dependencies is None and self.predecessors is None:
      self.precedes('anchor')

  def process_files(self, files: MarkdownFiles) -> None:
    context = Context(str(Path.cwd()))
    self._loader.init(context)
    self._renderer.init(context)

    if self._suite is None:
      modules = list(self._loader.load())
      for processor in self._processors:
        processor.process(modules, self)
      self._suite = ApiSuite(modules)

    for file in files:
      tags = [t for t in parse_block_tags(file.content) if t.name == 'pydoc']
      file.content = replace_tags(file.content, tags, lambda t: self._replace_pydoc_tag(self._suite, file, t))
      tags = [t for t in parse_inline_tags(file.content) if t.name == 'pylink']
      file.content = replace_tags(file.content, tags, lambda t: self._replace_pylink_tag(t))

  def _replace_pydoc_tag(self, suite: ApiSuite, file: MarkdownFile, tag: Tag) -> str | None:
    fqn = tag.args.strip()
    objects = suite.resolve_fqn(fqn)
    if len(objects) > 1:
      logger.warning('  found multiple matches for Python FQN <fg=cyan>%s</fg>', fqn)
    elif not objects:
      logger.warning('  found no match for Python FQN <fg=cyan>%s</fg>', fqn)
      return None

    import io
    fp = io.StringIO()
    self._renderer.render_object(fp, objects[0], tag.options)
    return self.action.repeat(file.path, file.output_path, fp.getvalue())

  def _replace_pylink_tag(self, tag: Tag) -> str | None:
    return f'{{@link pydoc:{tag.args.strip()}}}'
