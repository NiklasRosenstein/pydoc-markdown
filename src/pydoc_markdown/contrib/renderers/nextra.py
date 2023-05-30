# -*- coding: utf8 -*-

import dataclasses
import json
import logging
import os
import typing as t
from pathlib import Path

import docspec
import typing_extensions as te
from databind.core import DeserializeAs

from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class CustomizedMarkdownRenderer(MarkdownRenderer):
    """We override some defaults in this subclass."""

    #: Disabled because Docusaurus supports this automatically.
    insert_header_anchors: bool = False

    #: Escape html in docstring, otherwise it could lead to invalid html.
    escape_html_in_docstring: bool = True

    #: Conforms to Docusaurus header format.
    render_module_header_template: str = (
        "---\n" "sidebar_label: {relative_module_name}\n" "title: {module_name}\n" "---\n\n"
    )


@dataclasses.dataclass
class NextraRenderer(Renderer):
    """
    Produces Markdown files for use in a Nextra docs website.
    It creates files in a fixed layout that reflects the structure of the documented packages.
    The files will be rendered into the directory specified with the #docs_base_path option.

    ### Options
    """

    #: The #MarkdownRenderer configuration.
    markdown: te.Annotated[MarkdownRenderer, DeserializeAs(CustomizedMarkdownRenderer)] = dataclasses.field(
        default_factory=CustomizedMarkdownRenderer
    )

    #: The path where the Nextra docs content is. Defaults "docs" folder.
    docs_base_path: str = "docs"

    #: The output path inside the docs_base_path folder, used to output the
    #: module reference.
    relative_output_path: str = "pages"

    #: The sidebar path inside the docs_base_path folder, used to output the
    #: sidebar for the module reference.
    relative_sidebar_path: str = "sidebar.json"

    #: The top-level label in the sidebar. Default to 'Reference'. Can be set to null to
    #: remove the sidebar top-level all together. This option assumes that there is only one top-level module.
    sidebar_top_level_label: t.Optional[str] = "Reference"

    #: The top-level module label in the sidebar. Default to null, meaning that the actual
    #: module name will be used. This option assumes that there is only one top-level module.
    sidebar_top_level_module_label: t.Optional[str] = None

    def init(self, context: Context) -> None:
        self.markdown.init(context)

    def render(self, modules: t.List[docspec.Module]) -> None:
        module_tree: t.Dict[str, t.Any] = {"children": {}, "edges": []}
        output_path = Path(self.docs_base_path) / self.relative_output_path
        for module in modules:
            filepath = output_path

            module_parts = module.name.split(".")
            if module.location.filename.endswith("__init__.py"):
                module_parts.append("__init__")

            relative_module_tree = module_tree
            intermediary_module = []

            for module_part in module_parts[:-1]:
                # update the module tree
                intermediary_module.append(module_part)
                intermediary_module_name = ".".join(intermediary_module)
                relative_module_tree["children"].setdefault(intermediary_module_name, {"children": {}, "edges": []})
                relative_module_tree = relative_module_tree["children"][intermediary_module_name]

                # descend to the file
                filepath = filepath / module_part

            # create intermediary missing directories and get the full path
            filepath.mkdir(parents=True, exist_ok=True)
            filepath = filepath / f"{module_parts[-1]}.md"

            with filepath.open("w", encoding=self.markdown.encoding) as fp:
                logger.info("Render file %s", filepath)
                self.markdown.render_single_page(fp, [module])

            # only update the relative module tree if the file is not empty
            relative_module_tree["edges"].append(os.path.splitext(str(filepath.relative_to(self.docs_base_path)))[0])

