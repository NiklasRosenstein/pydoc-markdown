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

""" Utils for Pydoc-Markdown using the Watchdog library. """

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from typing import List, Tuple
import logging
import os
import threading

logger = logging.getLogger(__name__)


class _CallbackEventHandler(FileSystemEventHandler):

  def __init__(self, callback, filter_paths=None):
    self._callback = callback
    self._filter_paths = filter_paths

  def on_any_event(self, event):
    if self._filter_paths and event.src_path not in self._filter_paths:
      return
    self._callback(event)


def watch_paths(
  paths: List[str],
  recursive: bool = False
) -> Tuple[Observer, threading.Event]:
  """ Creates an observer for the specified *paths* and returns it together
  with a #threading.Event object. The event will be set when event occurred.
  """

  paths = [os.path.abspath(os.path.normpath(x)) for x in paths]
  directories = set(os.path.dirname(x) for x in paths)

  event = threading.Event()
  event_handler = _CallbackEventHandler(lambda _: event.set(), paths)
  observer = Observer()

  for directory in directories:
    observer.schedule(event_handler, directory, recursive)
  observer.start()

  return observer, event
