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

import dataclasses
import logging
import typing as t

import docspec
from typing_extensions import Protocol

from pydoc_markdown.contrib.processors.google import GoogleProcessor
from pydoc_markdown.contrib.processors.numpy import NumpyProcessor
from pydoc_markdown.contrib.processors.pydocmd import PydocmdProcessor
from pydoc_markdown.contrib.processors.sphinx import SphinxProcessor
from pydoc_markdown.interfaces import Processor, Resolver

logger = logging.getLogger(__name__)


class DelegatableProcessor(Protocol):
    def _process(self, node: docspec.ApiObject) -> None:
        ...


class CheckCapableProcessor(DelegatableProcessor, Protocol):
    def check_docstring_format(self, docstring: str) -> bool:
        ...


@dataclasses.dataclass
class SmartProcessor(Processor):
    """
    This processor picks the #GoogleProcessor, #SphinxProcessor, #PydocmdProcessor, or #NumpyProcessor after
    guessing which is appropriate from the syntax it finds in the docstring.
    """

    google: GoogleProcessor = dataclasses.field(default_factory=GoogleProcessor)
    pydocmd: PydocmdProcessor = dataclasses.field(default_factory=PydocmdProcessor)
    sphinx: SphinxProcessor = dataclasses.field(default_factory=SphinxProcessor)
    numpy: NumpyProcessor = dataclasses.field(default_factory=NumpyProcessor)

    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        docspec.visit(modules, self._process)

    def _process(self, obj: docspec.ApiObject):
        if not obj.docstring:
            return None

        object_name = ".".join(x.name for x in obj.path)
        object_type = type(obj).__name__

        processors: t.List[t.Tuple[str, DelegatableProcessor]] = [
            ("sphinx", self.sphinx),
            ("google", self.google),
            ("numpy", self.numpy),
            ("pydocmd", self.pydocmd),
        ]

        checkable_processors: t.List[t.Tuple[str, CheckCapableProcessor]] = [
            ("sphinx", self.sphinx),
            ("google", self.google),
            ("numpy", self.numpy),
        ]

        for name, processor in processors:
            indicator = "@doc:fmt:" + name
            if indicator in obj.docstring.content:
                logger.info("Using `%s` processor for %s `%s` (explicit)", name, object_type, object_name)
                obj.docstring.content = obj.docstring.content.replace(indicator, "")
                return processor._process(obj)

        for name, processor in checkable_processors:
            if processor.check_docstring_format(obj.docstring.content):
                logger.info("Using `%s` processor for %s `%s` (detected)", name, object_type, object_name)
                return processor._process(obj)

        logger.info("Using `pydocmd` processor for %s `%s` (default)", name, object_type, object_name)
        return self.pydocmd._process(obj)
