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

import collections
import contextlib
import csv
import hashlib
import os
import typing as t
from pathlib import Path

from nr.util.fs import is_relative_to

FilenameAndHash = collections.namedtuple('FilenameAndHash', 'algorithm,hash,name')


def hash_file(filename: str, algorithm: str, chunksize: int = 2**13) -> str:
  hash_ = hashlib.new(algorithm)
  with open(filename, 'rb') as fp:
    while True:
      data = fp.read(chunksize)
      if not data:
        break
      hash_.update(data)
  return hash_.hexdigest()


class KnownFiles:
  """
  A helper class to keep track of the files that you write so you can get back the
  list of files at a later point.
  """

  def __init__(self, directory: str, filename: str = '.generated-files.txt', hash_algorithm: str = 'md5') -> None:
    self._directory = directory
    self._filename = filename
    self._hash_algorithm = hash_algorithm
    self._files: t.Optional[t.List[str]] = None

  def __enter__(self) -> 'KnownFiles':
    assert self._files is None, 'Context already entered.'
    self._files = []
    return self

  def __exit__(self, *args) -> None:
    assert self._files is not None
    with open(os.path.join(self._directory, self._filename), 'w') as fp:
      writer = csv.writer(fp, delimiter=' ')
      for filename in self._files:
        try:
          hash_ = hash_file(os.path.join(self._directory, filename), self._hash_algorithm)
        except OSError:
          hash_ = '-'
        writer.writerow([self._hash_algorithm, hash_, filename])
    self._files = None

  def load(self) -> t.Iterable[FilenameAndHash]:
    try:
      with open(os.path.join(self._directory, self._filename), 'r') as fp:
        reader = csv.reader(fp, delimiter=' ')
        for row in reader:
          if len(row) != 3:
            continue
          algorithm, hash_, filename= row
          filename = os.path.join(self._directory, filename)
          yield FilenameAndHash(algorithm, hash_, filename)
    except FileNotFoundError:
      return; yield

  def _check_filename(self, filename: str) -> str:
    if not is_relative_to(filename, self._directory):
      raise ValueError('filename must point inside directory {!r}, got {!r}'
                       .format(self._directory, filename))
    return str(Path(filename).relative_to(self._directory))

  @contextlib.contextmanager
  def open(self, filename: str, mode: str = 'r', **kwargs) -> t.Generator[t.TextIO, None, None]:
    assert self._files is not None
    filename = self._check_filename(filename)
    assert 'b' not in mode, 'does not support binary file modes'
    if 'w' in mode or 'a' in mode:
      if self._files is None:
        raise RuntimeError('KnownFiles.__enter__() was not called')
      with open(os.path.join(self._directory, filename), mode, **kwargs) as fp:
        yield t.cast(t.TextIO, fp)
      self._files.append(filename)

  def append(self, filename: str) -> None:
    assert self._files is not None
    filename = self._check_filename(filename)
    open(os.path.join(self._directory, filename), 'r').close()  # Ensure the file exists.
    self._files.append(filename)
