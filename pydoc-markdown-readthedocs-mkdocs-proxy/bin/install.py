
"""
This script is executed when pydoc-markdown-mkdocs-proxy is installed. This should only run
from inside a readthedocs build process, thus it will assert that READTHEDOCS is actually set.
"""

import argparse
import os
import pipes
import stat
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--dry', action='store_true', help='Do not actually make changes on the filesystem.')
parser.add_argument('--rtd', action='store_true', help='Behave as if READTHEDOCS was set.')
args = parser.parse_args()

if not args.rtd and os.getenv('READTHEDOCS') != 'True':
  raise EnvironmentError(
    'READTHEDOCS must be {!r}, got {!r}.'.format('True', os.getenv('READTHEDOCS')))

new_executable = sys.executable + '-original'
if os.path.isfile(new_executable):
  print('appears to be already installed')
  sys.exit(0)

script = '''#!/bin/bash

if [[ "$1" == "-m" ]] && [[ "$2" == "mkdocs" ]] && [[ "$3" == "build" ]]; then
  shift
  shift
  {python} -c "from pydoc_markdown_readthedocs_mkdocs_proxy import main; main()" "$@"
else
  {python} "$@"
fi
exit $?
'''.format(python=pipes.quote(new_executable))

print('"{}" -> "{}"'.format(sys.executable, new_executable))
if not args.dry:
  os.rename(sys.executable, new_executable)
print('write "{}" with content'.format(sys.executable))
print('  ' + '\n  '.join(script.splitlines()))
if not args.dry:
  with open(sys.executable, 'w') as fp:
    fp.write(script)
  os.chmod(sys.executable, os.stat(sys.executable).st_mode | stat.S_IEXEC)
