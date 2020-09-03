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


@implements(Renderer)
class DocusaurusRenderer(Struct):
  """
  Produces Markdown files to be used with Docusaurus websites.

  ### Options
  """

  #: The #MarkdownRenderer configuration.
  markdown = Field(
    MarkdownRenderer,
    default=MarkdownRenderer(
      # disabled because Docusaurus supports this automatically
      insert_header_anchors=False,
      # escape html in docstring, otherwise it could lead to invalid html
      escape_html_in_docstring=True,
      # do not generate any page for empty modules
      skip_empty_modules=True,
      # conforms to Docusaurus header format
      render_module_header_template=(
        '---\n'
        'sidebar_label: {module_name}\n'
        'title: {module_name}\n'
        '---\n\n'
      )
    ),
  )

  #: The path where the docusaurus docs content is. Defaults "docs" folder.
  docs_base_path = Field(str, default='docs')

  #: The output path inside the docs_base_path folder, used to ouput the
  #: module reference.
  relative_output_path = Field(str, default='reference')

  #: The sidebar path inside the docs_base_path folder, used to ouput the
  #: sidebar for the module reference.
  relative_sidebar_path = Field(str, default='sidebar.json')

  #: The top-level label in the sidebar. Default to 'Reference'.
  sidebar_top_level_label = Field(str, default='Reference')

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

      # a bit dirty to cleanup the empty files like that, but hard to
      # hook into the rendering mechanism
      if self.markdown.skip_empty_modules and not filepath.read_text():
        filepath.unlink()
        continue

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
