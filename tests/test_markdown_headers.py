import pytest
import io

from pydocmd.document import Section


def test_preprocess_section():
  section = Section(None)
  section.depth = 1
  section.title = 'My Header'
  section.content = 'content'
  section.identifier = 'section-identifier'

  html_header_buffer = io.StringIO()
  section.render(html_header_buffer)
  assert html_header_buffer.getvalue() == "<h1 id=\"section-identifier\">My Header</h1>\n\ncontent\n"

  section.header_type = 'markdown'
  markdown_header_buffer = io.StringIO()
  section.render(markdown_header_buffer)
  assert markdown_header_buffer.getvalue() == "\n# My Header\ncontent\n"

  with pytest.raises(ValueError):
    section.header_type = 'invalid'
    section.render(markdown_header_buffer)
