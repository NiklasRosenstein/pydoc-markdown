
import io
import setuptools

with io.open('README.md', encoding='utf8') as fp:
  readme = fp.read()

with io.open('.config/classifiers.txt', encoding='utf8') as fp:
  classifiers = [x for x in fp.readlines() if x]

setuptools.setup(
  name = 'pydoc-markdown',
  version = '3.0.0',
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
  install_requires = [
    'nr.types>=1.1.1',
    'PyYAML>=3.12',
    'six>=0.11.0',
  ],
  entry_points = {
    'console_scripts': [
      'pydoc-markdown = pydoc_markdown.main:_entry_point',
    ]
  }
)
