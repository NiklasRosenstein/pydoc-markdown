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

import logging
import os
import subprocess
import typing as t
from pathlib import Path

import databind.core.dataclasses as dataclasses
import docspec
from nr.util.git import Git, NoCurrentBranchError

from pydoc_markdown.interfaces import Context, SourceLinker

logger = logging.getLogger(__name__)


def _getoutput(cmd: t.List[str], cwd: str = None) -> str:
  logger.debug('running command %r (cwd: %r)', cmd, cwd)
  process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE)
  stdout = process.communicate()[0].decode()
  if process.returncode != 0:
    raise RuntimeError('process {} exited with non-zero exit code {}'
                       .format(cmd[0], process.returncode))
  return stdout


def git_get_toplevel(cwd: str) -> str:
  return _getoutput(['git', 'rev-parse', '--show-toplevel'], cwd=cwd).strip()


def git_get_current_commit_sha(cwd: str) -> str:
  return _getoutput(['git', 'rev-parse', 'HEAD'], cwd=cwd).strip()


def git_get_current_branch(cwd: str) -> str:
  branches = _getoutput(['git', 'branch'], cwd=cwd).strip().splitlines()
  return next(b for b in branches if b.startswith('*')).split()[1]


@dataclasses.dataclass
class BaseGitSourceLinker(SourceLinker):
  """
  This is the base source linker for code in a Git repository.
  """

  #: The root directory, relative to the context directory. The context directory
  #: is usually the directory that contains Pydoc-Markdown configuration file.
  #: If not set, the project root will be determined from the Git repository in
  #: the context directory.
  root: t.Optional[str] = None

  #: Use the branch name instead of the current SHA to generate URLs.
  use_branch: bool = False

  def get_context_vars(self) -> t.Dict[str, str]:
    return {}

  def get_url_template(self) -> str:
    raise NotImplementedError

  # SourceLinker

  def get_source_url(self, obj: docspec.ApiObject) -> t.Optional[str]:
    """
    Compute the URL in the GitHub/Gitea #repo for the API object *obj*.
    """

    if not obj.location or not obj.location.filename:
      return None

    # Compute the path relative to the project root.
    try:
      rel_path = Path(obj.location.filename).relative_to(self._project_root)
    except ValueError:
      logger.debug('Ignored API object %s, path points outside of project root.', obj.name)
      return None

    context_vars = self.get_context_vars()
    context_vars['path'] = str(rel_path)
    context_vars['sha'] = (self._branch if self.use_branch else self._sha) or '?'
    context_vars['lineno'] = str(obj.location.lineno)

    url = self.get_url_template().format(**context_vars)

    logger.debug('Calculated URL for API object %s is %s', obj.name, url)
    return url

  # PluginBase

  def init(self, context: Context) -> None:
    """
    This is called before the rendering process. The source linker computes the project
    root and Git SHA at this stage before #get_source_url() is called.
    """

    git = Git(context.directory)

    if self.root:
      self._project_root = os.path.join(context.directory, self.root)
    else:
      project_root = git.get_toplevel()
      if not project_root:
        raise RuntimeError(f'Path "%s" is not in a Git repository', context.directory)
      self._project_root = project_root

    self._sha = git.rev_parse('HEAD')

    if self.use_branch:
      try:
        self._branch: str | None = git.get_current_branch_name()
        if '(' in self._branch:
          raise NoCurrentBranchError  # For older versions of nr.util which returned the detached HEAD branch
      except NoCurrentBranchError:
        logger.warning('Repository is not currently on a branch, falling back to SHA')
        self.use_branch = False
        self._branch = None

    logger.debug('project_root = %r', self._project_root)
    logger.debug('sha = %r', self._sha)
    logger.debug('branch = %r', self._branch)


@dataclasses.dataclass
class BaseGitServiceSourceLinker(BaseGitSourceLinker):

  #: The repository name, formatted as `owner/repo`.
  repo: str

  #: The host name of the Git service.
  host: str

  def get_context_vars(self) -> t.Dict[str, str]:
    return {'repo': self.repo, 'host': self.host}


@dataclasses.dataclass
class GitSourceLinker(BaseGitSourceLinker):
  """
  This source linker allows you to define your own URL template to generate a permalink for
  an API object.
  """

  #: The URL template as a Python format string. Available variables are "path", "sha" and "lineno".
  url_template: str

  def get_url_template(self) -> str:
    return self.url_template


@dataclasses.dataclass
class GiteaSourceLinker(BaseGitServiceSourceLinker):
  """
  Source linker for Git repositories hosted on gitea.com or any self-hosted Gitea instance.
  """

  host: str = "gitea.com"

  def get_url_template(self) -> str:
    return 'https://{host}/{repo}/src/commit/{sha}/{path}#L{lineno}'


@dataclasses.dataclass
class GithubSourceLinker(BaseGitServiceSourceLinker):
  """
  Source linker for Git repositories hosted on github.com or any self-hosted GitHub instance.
  """

  host: str = "github.com"

  def get_url_template(self) -> str:
    return 'https://{host}/{repo}/blob/{sha}/{path}#L{lineno}'


@dataclasses.dataclass
class GitlabSourceLinker(BaseGitServiceSourceLinker):
  """
  Source linker for Git repositories hosted on gitlab.com or any self-hosted Gitlab instance.
  """

  host: str = "gitlab.com"

  def get_url_template(self) -> str:
    return 'https://{host}/{repo}/-/blob/{sha}/{path}#L{lineno}'


@dataclasses.dataclass
class BitbucketSourceLinker(BaseGitServiceSourceLinker):
  """
  Source linker for Git repositories hosted on bitbucket.org or any self-hosted Bitbucket instance.
  """

  host: str = "bitbucket.org"

  def get_url_template(self) -> str:
    return 'https://{host}/{repo}/src/{sha}/{path}#lines-{lineno}'
