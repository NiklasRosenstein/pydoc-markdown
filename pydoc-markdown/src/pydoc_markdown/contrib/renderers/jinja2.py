
import dataclasses as D
import fnmatch
import logging
import os
import typing as t

import docspec
from docspec_python import format_arglist
import jinja2

from pydoc_markdown.contrib.renderers.markdown import MarkdownReferenceResolver
from pydoc_markdown.interfaces import Renderer, Resolver
from pydoc_markdown.util.docspec import format_function_signature, get_members_of_type, get_object_description

T = t.TypeVar('T')
log = logging.getLogger(__name__)


class Args(t.Dict[str, t.Any]):

  def get_render_args(self, modules: t.List[docspec.Module]) -> t.Dict[str, t.Any]:
    args = dict(self)
    if 'module' in args:
      try:
        args['module'] = next((m for m in modules if m.name == args['module']))
      except StopIteration:
        raise ValueError(f'module {args["module"]} not found')
    if 'modules' in args:
      args['modules'] = [m for m in modules if m.name in args['modules'] or any(fnmatch.fnmatch(m.name, x) for x in args['modules'])]
    return args


@D.dataclass
class RenderBlock:

  #: The path to the Jinja2 template that is used to render the output files.
  template: str

  #: A mapping for filename (without suffix) to a list of Module selectors.
  produces: t.Dict[str, Args]

  #: Settings for the Jinja2 Environment.
  jinja2_environment_settings: t.Dict[str, t.Any] = D.field(default_factory=dict)


@D.dataclass
class Jinja2Renderer(Renderer):

  #: Render instructions.
  renders: t.List[RenderBlock]

  #: Build directory where all the files are produced.
  build_directory: str = 'build/docs'

  def render(self, modules: t.List[docspec.Module]) -> None:
    # TODO (@NiklasRosenstein): Clean render support

    resolver = MarkdownReferenceResolver(modules)
    os.makedirs(self.build_directory, exist_ok=True)

    for render in self.renders:
      env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'), **render.jinja2_environment_settings)
      setup_env(env, resolver.reverse_map)
      env.filters['uid'] = resolver.generate_object_id
      template = env.get_template(render.template)
      for filename, args in render.produces.items():
        filename = os.path.join(self.build_directory, filename + '.md')
        log.info('Writing %s', filename)
        with open(filename, 'w') as fp:
          fp.write(template.render(**Args(args).get_render_args(modules)))  # TODO

  def get_resolver(self, modules: t.List[docspec.Module]) -> t.Optional[Resolver]:
    return MarkdownReferenceResolver(modules)


def setup_env(env: jinja2.Environment, reverse_map: docspec.ReverseMap) -> None:
  env.filters['classes'] = lambda modules: get_members_of_type(modules, docspec.Class)
  env.filters['functions'] = lambda objs: get_members_of_type(objs, docspec.Function)
  env.filters['attrs'] = lambda objs: get_members_of_type(objs, docspec.Data)
  env.filters['indent'] = _indent_filter
  env.filters['blockquote'] = _blockquote_filter
  env.filters['first_line'] = _first_line_filter
  env.filters['format_arglist'] = format_arglist
  env.filters['format_function_signature'] = format_function_signature
  env.filters['describe'] = lambda obj: get_object_description(obj, reverse_map)


def _indent_filter(text: t.Optional[str], level: int = 1, ) -> str:
  if not text: return ''
  lines = text.splitlines()
  return '\n'.join(lines[:1] + list('    ' * level + l for l in lines[1:]))


def _blockquote_filter(text: t.Optional[str]) -> str:
  if not text: return ''
  return '> ' + '\n> '.join(text.splitlines())


def _first_line_filter(text: t.Optional[str]) -> str:
  if not text: return ''
  return text.splitlines()[0]
