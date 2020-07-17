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

from nr.databind.core import Field, Struct
from nr.interface import implements, override
from pydoc_markdown.interfaces import Context, SourceLinker
from typing import List, Optional, Tuple
import docspec
import logging
import os
import nr.fs
import subprocess

logger = logging.getLogger(__name__)


def _getoutput(cmd: List[str], cwd: str = None) -> str:
  logger.debug('running command %r (cwd: %r)', cmd, cwd)
  process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE)
  stdout = process.communicate()[0].decode()
  if process.returncode != 0:
    raise RuntimeError('process {} exited with non-zero exit code {}'
                       .format(cmd[0], process.returncode))
  return stdout


@implements(SourceLinker)
class GitHubSourceLinker(Struct):
  """
  This is a source linker for code on a GitHub repository. It calculates the URL using
  the source filename relative to the repository root (determined from the current working
  directory) and the ``HEAD`` commit's SHA.
  """

  #: The Git repository owner and name.
  repo = Field(str)

  #: The Github hostname. Defaults to `"github.com"`.
  host = Field(str, default='github.com')

  #: The root directory, relative to the context directory. The context directory
  #: is usually the directory that contains Pydoc-Markdown configuration file.
  #: If not set, the project root will be determined from the Git repository in
  #: the context directory.
  root = Field(str, default=None)

  URL_TEMPLATE = 'https://{host}/{repo}/blob/{sha}/{path}#L{lineno}'

  # SourceLinker

  @override
  def get_source_url(self, obj: docspec.ApiObject) -> str:
    """
    Compute the URL in the GitHub #repo for the API object *obj*.
    """

    if not obj.location:
      return None

    # Compute the path relative to the project root.
    rel_path = os.path.relpath(os.path.abspath(obj.location.filename), self._project_root)
    if not nr.fs.issub(rel_path):
      logger.debug('Ignored API object %s, path points outside of project root.', obj.name)
      return None

    url = self.URL_TEMPLATE.format(
      host=self.host, repo=self.repo, sha=self._sha, path=rel_path, lineno=obj.location.lineno)

    logger.debug('Calculated URL for API object %s is %s', obj.name, url)
    return url

  # PluginBase

  @override
  def init(self, context: Context) -> None:
    """
    This is called before the rendering process. The source linker computes the project
    root and Git SHA at this stage before #get_source_url() is called.
    """

    if self.root:
      self._project_root = os.path.join(context.directory, self.root)
    else:
      self._project_root = _getoutput(['git', 'rev-parse', '--show-toplevel'], cwd=context.directory).strip()
    self._sha = _getoutput(['git', 'rev-parse', 'HEAD'], cwd=self._project_root).strip()
    logger.debug('project_root = %r', self._project_root)
    logger.debug('sha = %r', self._sha)
