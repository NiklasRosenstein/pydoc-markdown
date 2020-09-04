# -*- coding: utf8 -*-
from nr.databind.core import Field, Struct
from nr.interface import implements, override
from pathlib import Path
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from typing import Any, Dict, List, Text
import docspec
import json
import os.path


class CustomizedMarkdownRenderer(MarkdownRenderer):
  """We override some defaults in this subclass. """

  #: Disabled because Docusaurus supports this automatically.
  insert_header_anchors = Field(bool, default=False)

  #: Escape html in docstring, otherwise it could lead to invalid html.
  escape_html_in_docstring = Field(bool, default=True)

  #: Conforms to Docusaurus header format.
  render_module_header_template = Field(str, default=(
    '---\n'
    'sidebar_label: {module_name}\n'
    'title: {module_name}\n'
    '---\n\n'
  ))


@implements(Renderer)
class DocusaurusRenderer(Struct):
  """
  Produces Markdown files and a `sidebar.json` file for use in a [Docusaurus v2][1] websites.
  It creates files in a fixed layout that reflects the structure of the documented packages.
  The files will be rendered into the directory specified with the #docs_base_path option.

  Check out the complete [Docusaurus example on GitHub][2].

  [1]: https://v2.docusaurus.io/
  [2]: https://github.com/NiklasRosenstein/pydoc-markdown/tree/develop/examples/docusaurus

  ### Options
  """

  #: The #MarkdownRenderer configuration.
  markdown = Field(CustomizedMarkdownRenderer, default=CustomizedMarkdownRenderer)

  #: The path where the docusaurus docs content is. Defaults "docs" folder.
  docs_base_path = Field(str, default='docs')

  #: The output path inside the docs_base_path folder, used to ouput the
  #: module reference.
  relative_output_path = Field(str, default='reference')

  #: The sidebar path inside the docs_base_path folder, used to ouput the
  #: sidebar for the module reference.
  relative_sidebar_path = Field(str, default='sidebar.json')

  #: The top-level label in the sidebar. Default to 'Reference'. Can be set to null to
  #: remove the sidebar top-level all together.
  sidebar_top_level_label = Field(str, default='Reference', nullable=True)

  @override
  def render(self, modules: List[docspec.Module]) -> None:
    modules_and_paths = []
    module_tree = {"children": {}, "edges": []}
    output_path = Path(self.docs_base_path) / self.relative_output_path
    for module in modules:
      filepath = output_path

      module_parts = module.name.split(".")
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

      with filepath.open('w') as fp:
        self.markdown.render_to_stream([module], fp)

      # only update the relative module tree if the file is not empty
      relative_module_tree["edges"].append(
        os.path.splitext(str(filepath.relative_to(self.docs_base_path)))[0]
      )

    self._render_side_bar_config(module_tree)

  def _render_side_bar_config(self, module_tree: Dict[Text, Any]) -> None:
    """
    Render sidebar configuration in a JSON file. See Docusaurus sidebar structure:

    https://v2.docusaurus.io/docs/docs-introduction/#sidebar
    """
    sidebar = {
      "type": 'category',
      "label": self.sidebar_top_level_label,
    }
    self._build_sidebar_tree(sidebar, module_tree)
    if not self.sidebar_top_level_label:
      sidebar = sidebar['items']

    sidebar_path = Path(self.docs_base_path) / self.relative_output_path / self.relative_sidebar_path
    with sidebar_path.open("w") as handle:
      json.dump(sidebar, handle, indent=2, sort_keys=True)

  def _build_sidebar_tree(self, sidebar: Dict[Text, Any], module_tree: Dict[Text, Any]) -> None:
    """
    Recursively build the sidebar tree, it follows Docusaurus sidebar structure:

    https://v2.docusaurus.io/docs/docs-introduction/#sidebar
    """
    sidebar["items"] = module_tree.get("edges", [])
    for child_name, child_tree in module_tree.get("children", {}).items():
      child = {
          "type": 'category',
          "label": child_name,
      }
      self._build_sidebar_tree(child, child_tree)
      sidebar["items"].append(child)
