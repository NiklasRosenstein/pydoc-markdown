
import io
import re
import setuptools
import sys

with io.open('pydocmd/__init__.py', encoding='utf8') as fp:
  version = re.search(r"__version__\s*=\s*'(.*)'", fp.read()).group(1)

with io.open('README.md', encoding='utf8') as fp:
  long_description = fp.read()

requirements = ['MkDocs>=1.0.0', 'Markdown>=2.6.11', 'PyYAML>=3.12', 'six>=0.11.0', 'yapf>=0.26.0']

setuptools.setup(
  name = 'pydoc-markdown',
  version = version,
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'Create Python API documentation in Markdown format',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  url = 'https://github.com/NiklasRosenstein/pydoc-markdown',
  license = 'MIT',
  packages = setuptools.find_packages('.', ['test', 'test.*', 'docs', 'docs.*']),
  package_dir = {'': '.'},
  include_package_data = False,
  install_requires = requirements,
  extras_require = {},
  tests_require = [],
  python_requires = None, # TODO: '>=3.4,<4.0.0',
  data_files = [],
  entry_points = {
    'console_scripts': [
      'pydocmd=pydocmd.__main__:main',
    ]
  },
  cmdclass = {},
  keywords = ['markdown', 'pydoc', 'generator', 'docs', 'documentation'],
  classifiers = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Intended Audience :: End Users/Desktop', 'Topic :: Software Development :: Code Generators', 'Topic :: Utilities', 'License :: OSI Approved :: MIT License', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.3', 'Programming Language :: Python :: 3.4', 'Programming Language :: Python :: 3.5'],
)
