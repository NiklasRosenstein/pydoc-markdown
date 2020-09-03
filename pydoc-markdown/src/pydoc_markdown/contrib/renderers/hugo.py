# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from nr.databind.core import Field, ProxyType, Remainder, Struct
from nr.interface import implements, override
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer, Resolver, Server, Builder
from pydoc_markdown.util.knownfiles import KnownFiles
from pydoc_markdown.util.pages import Page
from urllib.parse import urlparse, urljoin
from typing import Dict, Iterable, List, Optional, TextIO
import docspec
import logging
import nr.fs
import os
import platform as _platform
import posixpath
import requests
import shutil
import subprocess
import sys
import tarfile
import toml
import yaml

logger = logging.getLogger(__name__)
HugoPage = ProxyType()


@HugoPage.implementation
class HugoPage(Page):
  """
  A subclass of #Page which adds Hugo-specific overrides.

  ### Options
  """

  children = Field([HugoPage], default=list)

  #: The Hugo preamble of the page. This is merged with the #HugoRenderer.default_preamble.
  preamble = Field(dict, default=dict)

  #: Override the directory that this page is rendered into (relative to the
  #: content directory). Defaults to `null`.
  directory = Field(str, default=None)


class HugoThemePath(Struct):
  path = Field(str)

  @property
  def name(self):
    return os.path.basename(self.path)

  def install(self, themes_dir: str):
    # TODO (@NiklasRosenstein): Support Windows (which does not support symlinking).
    dst = os.path.join(self.name)
    if not os.path.lexists(dst):
      os.symlink(self.path, dst)


class HugoThemeGitUrl(Struct):
  clone_url = Field(str)
  postinstall = Field([str], default=list)

  @property
  def name(self):
    return posixpath.basename(self.clone_url).rstrip('.git').lstrip('hugo-')

  def install(self, theme_dir: str):
    dst = os.path.join(theme_dir, self.name)
    if not os.path.isdir(dst):
      command = ['git', 'clone', self.clone_url, dst, '--depth', '1',
                 '--recursive', '--shallow-submodules']
      subprocess.check_call(command)
      for command in self.postinstall:
        subprocess.check_call(command, shell=True, cwd=dst)


class HugoConfig(Struct):
  """
  Represents the Hugo configuration file that is rendered into the build directory.

  ### Options
  """

  #: Base URL.
  baseURL = Field(str, default=None)

  #: Language code. Default: `en-us`
  languageCode = Field(str, default='en-us')

  #: Title of the site. This is a mandatory field.
  title = Field(str)

  #: The theme of the site. This is a mandatory field. It must be a string, a #HugoThemePath
  #: or a #HugoThemeGitUrl object. Examples:
  #:
  #: ```yml
  #: theme: antarctica
  #: theme: {clone_url: "https://github.com/alex-shpak/hugo-book.git"}
  #: theme: docs/hugo-theme/
  #: ```
  theme = Field((str, HugoThemePath, HugoThemeGitUrl))

  #: This field collects all remaining options that do not match any of the above
  #: and will be forwarded directly into the Hugo `config.yaml` when it is rendered
  #: into the build directory.
  additional_options = Field(dict, Remainder())

  def to_toml(self, fp: TextIO) -> None:
    data = self.additional_options.copy()
    for field in self.__fields__:
      if field in ('additional_options', 'theme'):
        continue
      value = getattr(self, field)
      if value:
        data[field] = value
    if isinstance(self.theme, str):
      data['theme'] = self.theme
    elif isinstance(self.theme, (HugoThemePath, HugoThemeGitUrl)):
      data['theme'] = self.theme.name
    else: assert False
    fp.write(toml.dumps(data))


@implements(Renderer, Server, Builder)
class HugoRenderer(Struct):
  """
  A renderer that produces Markdown files compatible with [Hugo][0]. The `--bootstrap hugo`
  option can be used to create a Pydoc-Markdown configuration file with the Hugo template.

  * Adds a YAML preamble to every generated Markdown file.
  * Produces files in a layout suitable for Hugo (e.g. `_index.md` files).
  * Produces a `config.yaml` if #config is not set to `null`.
  * Can be used with the Pydoc-Markdown `--server` option to live-preview the generated docs.
  * Downloads a suitable Hugo binary from Github if Hugo is not already installed (see #get_hugo).

  Example configuration:

  ```yml
  renderer:
    type: hugo
    config:
      title: My Project
      theme: {clone_url: "https://github.com/alex-shpak/hugo-book.git"}
    # The "book" theme only renders pages in "content/docs" into the nav.
    content_directory: content/docs
    default_preamble: {menu: main}
    pages:
      - title: Home
        name: index
        source: README.md
      - title: API Documentation
        contents:
          - '*'
  ```

  [0]: https://gohugo.io/

  ### Options
  """

  #: The directory where all generated files are placed. Default: `build/docs`
  build_directory = Field(str, default='build/docs')

  #: The directory _inside_ the build directory where the generated
  #: pages are written to. Default: `content`
  content_directory = Field(str, default='content')

  #: Clean up files that were previously generated by the renderer before the next
  #: render pass. Defaults to `True`.
  clean_render = Field(bool, default=True)

  #: The pages to render.
  pages = Field(HugoPage.collection_type())

  #: The default Hugo preamble that is applied to every page. Example:
  #:
  #: ```yml
  #: default_preamble:
  #:   menu: main
  #: ```
  default_preamble = Field(dict, default=dict)

  #: The #MarkdownRenderer configuration.
  markdown = Field(MarkdownRenderer, default=Field.DEFAULT_CONSTRUCT)

  #: The contents of the Hugo `config.toml` file as YAML. This can be set to `null` in
  #: order to not produce the `config.toml` file in the #build_directory. Must be deserializable
  #: into a #HugoConfig.
  config = Field(HugoConfig, nullable=True)

  #: Options for when the Hugo binary is not present and should be downloaded
  #: automatically. Example:
  #:
  #: ```yml
  #: get_hugo:
  #:   enabled: true
  #:   version: '0.71'
  #:   extended: true
  #: ```
  get_hugo = Field({
    'enabled': Field(bool, default=True),
    'version': Field(str, default=None),
    'extended': Field(bool, default=True),
  }, default=Field.DEFAULT_CONSTRUCT)

  _context = Field(Context, default=None, hidden=True)  # Initialized in #init()

  def _render_page(self, modules: List[docspec.Module], page: HugoPage, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    preamble = dict(**self.default_preamble, **{'title': page.title}, **page.preamble)

    with open(filename, 'w') as fp:
      fp.write('---\n')
      fp.write(yaml.safe_dump(preamble))
      fp.write('---\n\n')

      if page.source:
        with open(os.path.join(self._context.directory, page.source)) as src:
          shutil.copyfileobj(src, fp)
      else:
        self.markdown.render_to_stream(modules, fp)

  def _get_hugo_bin(self):
    hugo_bin = shutil.which('hugo')
    if not hugo_bin and self.get_hugo.enabled:
      hugo_bin = os.path.abspath(os.path.join(self.build_directory, '.bin', 'hugo'))
      if not os.path.isfile(hugo_bin):
        install_hugo(hugo_bin, self.get_hugo.version, self.get_hugo.extended)
    if not hugo_bin:
      raise RuntimeError('Hugo is not installed')
    return hugo_bin

  # Renderer

  @override
  def render(self, modules: List[docspec.Module]) -> None:
    known_files = KnownFiles(self.build_directory)
    content_dir = os.path.join(self.build_directory, self.content_directory)

    if self.clean_render:
      for file_ in known_files.load():
        try:
          os.remove(file_.name)
        except FileNotFoundError as exc:
          pass

    # Render the pages.
    with known_files:
      for item in self.pages.iter_hierarchy():
        if item.page.name == 'index':
          item.page.name = '_index'
        page_content_dir = content_dir
        if item.page.directory:
          page_content_dir = os.path.normpath(os.path.join(content_dir, item.page.directory))
        filename = item.filename(page_content_dir, '.md', index_name='_index', skip_empty_pages=False)
        self._render_page(item.page.filtered_modules(modules), item.page, filename)
        known_files.append(filename)

      # Render the config file.
      if self.config is not None:
        if isinstance(self.config.theme, (HugoThemePath, HugoThemeGitUrl)):
          self.config.theme.install(os.path.join(self.build_directory, 'themes'))
        filename = os.path.join(self.build_directory, 'config.toml')
        logger.info('Rendering "%s"', filename)
        with known_files.open(filename, 'w') as fp:
          self.config.to_toml(fp)

  @override
  def get_resolver(self, modules: List[docspec.Module]) -> Optional[Resolver]:
    # TODO (@NiklasRosenstein): The resolver returned by the Markdown
    #   renderer does not implement linking across multiple pages.
    return self.markdown.get_resolver(modules)

  # Server

  @override
  def get_server_url(self) -> str:
    urlinfo = urlparse(self.config.baseURL or '')
    return urljoin('http://localhost:1313/', urlinfo.path)

  @override
  def start_server(self) -> subprocess.Popen:
    hugo_bin = self._get_hugo_bin()
    command = [hugo_bin, 'server']
    logger.info('Running %s in "%s"', command, self.build_directory)
    return subprocess.Popen(command, cwd=self.build_directory)

  # Builder

  @override
  def build(self, site_dir: str=None) -> None:
    command = [self._get_hugo_bin()]
    if site_dir:
      command += ['--destination', os.path.abspath(site_dir)]
    subprocess.check_call(command, cwd=self.build_directory)

  # PluginBase

  @override
  def init(self, context: Context) -> None:
    self._context = context
    self.markdown.init(context)


def install_hugo(to: str, version: str = None, extended: bool = True) -> None:
  """
  Downloads the latest release of *Hugo* from [Github](https://github.com/gohugoio/hugo/releases)
  and places it at the path specified by *to*. This will install the extended version if it is
  available and *extended* is set to `True`.

  :param to: The file to write the Hugo binary to.
  :param version: The Hugo version to get. If not specified, the latest release will be used.
  :param extended: Whether to download the "Hugo extended" version. Defaults to True.
  """

  # TODO (@NiklasRosenstein): Support BSD platforms.

  if sys.platform.startswith('linux'):
    platform = 'Linux'
  elif sys.platform.startswith('win32'):
    platform = 'Windows'
  elif sys.platform.startswith('darwin'):
    platform = 'macOS'
  else:
    raise EnvironmentError('unsure how to get a Hugo binary for platform {!r}'.format(sys.platform))

  machine = _platform.machine().lower()
  if machine in ('x86_64', 'amd64'):
    arch = '64bit'
  elif machine in ('i386',):
    arch = '32bit'
  else:
    raise EnvironmentError('unsure whether to intepret {!r} as 32- or 64-bit.'.format(machine))

  releases = get_github_releases('gohugoio/hugo')
  if version:
    version = version.lstrip('v')
    for release in releases:
      if release['tag_name'].lstrip('v') == version:
        break
    else:
      raise ValueError('no Hugo release for version {!r} found'.format(version))
  else:
    release = next(releases)
    version = release['tag_name'].lstrip('v')

  files = {asset['name']: asset['browser_download_url'] for asset in release['assets']}

  hugo_archive = 'hugo_{}_{}-{}.tar.gz'.format(version, platform, arch)
  hugo_extended_archive = 'hugo_extended_{}_{}-{}.tar.gz'.format(version, platform, arch)
  if extended and hugo_extended_archive in files:
    filename = hugo_extended_archive
  else:
    filename = hugo_archive

  logger.info('Downloading Hugo v%s from "%s"', version, files[filename])
  os.makedirs(os.path.dirname(to), exist_ok=True)
  with nr.fs.tempdir() as tempdir:
    path = os.path.join(tempdir.name, filename)
    with open(path, 'wb') as fp:
      shutil.copyfileobj(requests.get(files[filename], stream=True).raw, fp)
    with tarfile.open(path) as archive:
      with open(to, 'wb') as fp:
        shutil.copyfileobj(archive.extractfile('hugo'), fp)

  nr.fs.chmod(to, '+x')
  logger.info('Hugo v%s installed to "%s"', version, to)


def get_github_releases(repo: str) -> Iterable[dict]:
  """
  Returns an iterator for all releases of a Github repository.
  """

  url = 'https://api.github.com/repos/{}/releases'.format(repo)
  while url:
    response = requests.get(url)
    links = parse_links_header(response.headers.get('Link'))
    url = links.get('next')
    yield from response.json()


def parse_links_header(link_header: str) -> Dict[str, str]:
  """
  Parses the `Link` HTTP header and returns a map of the links. Logic from
  [PageLinks.java](https://github.com/eclipse/egit-github/blob/master/org.eclipse.egit.github.core/src/org/eclipse/egit/github/core/client/PageLinks.java#L43-75).
  """

  links = {}

  for link in link_header.split(','):
    segments = link.split(';')
    if len(segments) < 2:
      continue
    link_part = segments[0].strip()
    if not link_part.startswith('<') or not link_part.endswith('>'):
      continue
    link_part = link_part[1:-1]
    for rel in (x.strip().split('=') for x in segments[1:]):
      if len(rel) < 2 or rel[0] != 'rel':
        continue
      rel_value = rel[1]
      if rel_value.startswith('"') and rel_value.endswith('"'):
        rel_value = rel_value[1:-1]
      links[rel_value] = link_part

  return links
