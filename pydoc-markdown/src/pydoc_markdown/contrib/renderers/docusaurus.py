# -*- coding: utf8 -*-
from nr.databind.core import Field
from nr.interface import implements, override
from pathlib import Path
from pydoc_markdown.interfaces import Renderer
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from typing import Any, Dict, List, Text
import docspec
import json
import os.path


@implements(Renderer)
class DocusaurusRenderer(MarkdownRenderer):
  """
  Produces Markdown files. This renderer is often used by other renderers, such as
  #MkdocsRenderer and #HugoRenderer. It provides a wide variety of options to customize
  the generated Markdown files.

  ### Options
  """

  #: If enabled, inserts anchors before Markdown headers to ensure that
  #: links to the header work. This is disabled by default because Docusaurus
  #: supports this automatically.
  insert_header_anchors = Field(bool, default=False)

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

  #: Skip documenting modules if empty. Defaults to True.
  skip_empty_modules = Field(bool, default=True)

  #: Escape html in docstring. Default to True.
  escape_html_in_docstring = Field(bool, default=True)

  def _render_header(self, fp, level, obj):
    if isinstance(obj, docspec.Module):
      fp.write('---\n')
      fp.write(f'sidebar_label: {obj.name}\n')
      fp.write(f'title: {obj.name}\n')
      fp.write('---\n\n')
      return

    super(DocusaurusRenderer, self)._render_header(fp, level, obj)

  def _render_recursive(self, fp, level, obj):
    members = getattr(obj, 'members', [])
    if self.skip_empty_modules and isinstance(obj, docspec.Module) and not members:
      return

    return super(DocusaurusRenderer, self)._render_recursive(fp, level, obj)

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

      with filepath.open('w', encoding=self.encoding) as fp:
        self._render_modules([module], fp)

      # a bit dirty to cleanup the empty files like that, but hard to
      # hook into the rendering mechanism
      if self.skip_empty_modules and not filepath.read_text():
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
