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
from pydoc_markdown.interfaces import SourceLinker
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

  def _get_repo_root(self) -> Optional[str]:
    if hasattr(self, '_repo_root'):
      return self._repo_root
    self._repo_root = _getoutput(['git', 'rev-parse', '--show-toplevel']).strip()
    logger.debug('repo root = %r', self._repo_root)
    return self._repo_root

  def _get_sha(self) -> str:
    if hasattr(self, '_sha'):
      return self._sha
    self._sha = _getoutput(['git', 'rev-parse', 'HEAD']).strip()
    logger.debug('sha = %r', self._sha)
    return self._sha

  @override
  def get_source_url(self, obj: docspec.ApiObject) -> str:
    if not obj.location:
      return None
    repo_root = self._get_repo_root()
    if not repo_root:
      return None
    sha = self._get_sha()
    rel_path = os.path.relpath(os.path.abspath(obj.location.filename), repo_root)
    if not nr.fs.issub(rel_path):
      # The path points outside of the repo_root. Cannot construct the URL in that case.
      logger.debug('rel_path %r points outside of repo_root %r', rel_path, repo_root)
      return None
    url = 'https://{}/{}/blob/{}/{}#L{}'.format(
      self.host, self.repo, sha, rel_path, obj.location.lineno)
    logger.debug('url for api object %r: %r (rel_path: %r)', obj.name, url, rel_path)
    return url
