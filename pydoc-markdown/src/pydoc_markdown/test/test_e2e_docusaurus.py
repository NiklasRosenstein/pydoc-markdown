import json
from pathlib import Path

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.docusaurus import DocusaurusRenderer
from .test_utils import assert_text_equals


def test_full_processing():
    docs_path = Path(__file__).parent / "test_package" / "docs"
    config = PydocMarkdown(
        loaders=[PythonLoader(
            search_path=[str(Path(__file__).parent.resolve())],
            packages=['test_package']
        )],
        processors=[FilterProcessor(skip_empty_modules=True), CrossrefProcessor(), SmartProcessor()],
        renderer=DocusaurusRenderer(
        docs_base_path=str(docs_path.resolve()),
        sidebar_top_level_label="Code reference"
    ))

    modules = config.load_modules()
    config.process(modules)
    config.render(modules)

    sidebar = docs_path / "reference" / "sidebar.json"
    suff_md = docs_path / "reference" / "test_package" / "module" / "stuff.md"
    assert (docs_path / "reference").is_dir()
    assert sidebar.exists()
    assert suff_md.exists()
    assert not (docs_path / "reference" / "test_package" / "no_docstrings.md").exists()

    with sidebar.open("r") as handle:
        sidebar = json.load(handle)

    assert sidebar == {
      "items": [
        {
          "items": [
            {
              "items": [
                "reference/test_package/module/stuff"
              ],
              "label": "test_package.module",
              "type": "category"
            }
          ],
          "label": "test_package",
          "type": "category"
        }
      ],
      "label": "Code reference",
      "type": "category"
    }

    with suff_md.open("r") as handle:
        stuff_doc = handle.read()

    assert_text_equals(stuff_doc, r"""---
sidebar_label: test_package.module.stuff
title: test_package.module.stuff
---

This is a module about stuff.

#### CONSTANT

this is a constant about stuff

#### my\_funct

```python
my_funct()
```

Do something, or nothing.

## CoolStuff Objects

```python
class CoolStuff()
```

Super cool stuff.

#### cool\_attr

This is a cool attribute.

#### run\_cool\_stuff

```python
 | run_cool_stuff()
```

Run cool stuff
""")
