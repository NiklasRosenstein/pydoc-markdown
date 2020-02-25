
import io
import re
import setuptools
import sys

with io.open('src/pydoc_markdown/__init__.py', encoding='utf8') as fp:
  version = re.search(r"__version__\s*=\s*'(.*)'", fp.read()).group(1)

with io.open('README.md', encoding='utf8') as fp:
  long_description = fp.read()

requirements = ['nr.databind >=0.0.1,<0.1.0', 'six >=0.11.0,<1.0.0', 'PyYAML >=5.3,<6.0.0']

setuptools.setup(
  name = 'pydoc-markdown',
  version = version,
  author = None,
  author_email = None,
  description = 'Create Python API documentation in Markdown format.',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  url = 'https://github.com/NiklasRosenstein/pydoc-markdown',
  license = 'MIT',
  packages = setuptools.find_packages('src', ['test', 'test.*', 'docs', 'docs.*']),
  package_dir = {'': 'src'},
  include_package_data = False,
  install_requires = requirements,
  extras_require = {},
  tests_require = [],
  python_requires = None, # TODO: None,
  data_files = [],
  entry_points = {
    'console_scripts': [
      'pydoc-markdown = pydoc_markdown.main:_entry_point',
    ],
    'pydoc_markdown.interfaces.Loader': [
      'python = pydoc_markdown.contrib.loaders.python:PythonLoader',
    ],
    'pydoc_markdown.interfaces.Processor': [
      'filter = pydoc_markdown.contrib.processors.filter:FilterProcessor',
      'pydocmd = pydoc_markdown.contrib.processors.pydocmd:PydocmdProcessor',
      'sphinx = pydoc_markdown.contrib.processors.pydocmd:SphinxProcessor',
    ],
    'pydoc_markdown.interfaces.Renderer': [
      'markdown = pydoc_markdown.contrib.renderers.markdown:MarkdownRenderer',
      'mkdocs = pydoc_markdown.contrib.renderers.mkdocs:MkDocsRenderer',
    ]
  },
  cmdclass = {}
)
