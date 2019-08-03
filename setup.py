
import io
import re
import setuptools

with io.open('src/pydoc_markdown/__init__.py', encoding='utf8') as fp:
  version = re.search(r"__version__\s*=\s*'(.*)'", fp.read()).group(1)

with io.open('README.md', encoding='utf8') as fp:
  readme = fp.read()

with io.open('.config/classifiers.txt', encoding='utf8') as fp:
  classifiers = [x for x in fp.readlines() if x]

setuptools.setup(
  name = 'pydoc-markdown',
  version = version,
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  license = 'MIT',
  url = 'https://github.com/NiklasRosenstein/pydoc-markdown',
  description = 'Create Python API documentation in Markdown format.',
  long_description = readme,
  long_description_content_type = 'text/markdown',
  classifiers = classifiers,
  keywords = 'markdown pydoc generator docs documentation',
  packages = setuptools.find_packages('src'),
  package_dir = {'': 'src'},
  install_requires = ['nr.types>=2.3.0', 'pyyaml>=3.12', 'six>=0.11.0'],
  entry_points = {
    'console_scripts': [
      'pydoc-markdown = pydoc_markdown.main:_entry_point',
    ],
    'pydoc_markdown.interfaces.Loader': [
      'python = pydoc_markdown.contrib.loaders.python:PythonLoader',
    ],
    'pydoc_markdown.interfaces.Processor': [
      'pydocmd = pydoc_markdown.contrib.processors.pydocmd:PydocmdProcessor',
      'sphinx = pydoc_markdown.contrib.processors.pydocmd:SphinxProcessor',
    ],
    'pydoc_markdown.interfaces.Renderer': [
      'markdown = pydoc_markdown.contrib.renderers.markdown:MarkdownRenderer',
      'mkdocs = pydoc_markdown.contrib.renderers.mkdocs:MkDocsRenderer',
    ]
  }
)
