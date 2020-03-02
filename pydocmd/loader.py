# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
This module provides implementations to load documentation information from
an identifier as it is specified in the `pydocmd.yml:generate` configuration
key. A loader basically takes care of loading the documentation content for
that name, but is not supposed to apply preprocessing.
"""

from __future__ import print_function
from .imp import import_object_with_scope
import collections
import inspect
import types
import uuid
from yapf.yapflib.yapf_api import FormatCode

function_types = (types.FunctionType, types.LambdaType, types.MethodType,
  types.BuiltinFunctionType, types.BuiltinMethodType)
if hasattr(types, 'UnboundMethodType'):
  function_types += (types.UnboundMethodType,)


NotSet = object()


def trim(docstring):
  if not docstring:
    return ''
  lines = [x.rstrip() for x in docstring.split('\n')]
  lines[0] = lines[0].lstrip()

  indent = None
  for i, line in enumerate(lines):
    if i == 0 or not line: continue
    new_line = line.lstrip()
    delta = len(line) - len(new_line)
    if indent is None:
      indent = delta
    elif delta > indent:
      new_line = ' ' * (delta - indent) + new_line
    lines[i] = new_line

  return '\n'.join(lines)


class PythonLoader(object):
  """
  Expects absolute identifiers to import with #import_object_with_scope().
  """
  def __init__(self, config):
    self.config = config

  def load_section(self, section):
    """
    Loads the contents of a #Section. The `section.identifier` is the name
    of the object that we need to load.

    # Arguments
      section (Section): The section to load. Fill the `section.title` and
        `section.content` values. Optionally, `section.loader_context` can
        be filled with custom arbitrary data to reference at a later point.
    """

    assert section.identifier is not None
    obj, scope = import_object_with_scope(section.identifier)

    if '.' in section.identifier:
      default_title = section.identifier.rsplit('.', 1)[1]
    else:
      default_title = section.identifier

    section.title = getattr(obj, '__name__', default_title)
    section.content = trim(get_docstring(obj))
    section.loader_context = {'obj': obj, 'scope': scope}

    # Add the function signature in a code-block.
    if callable(obj):
      sig = get_function_signature(obj, scope if inspect.isclass(scope) else None)
      section.content = '```python\n{}\n```\n'.format(sig.strip()) + section.content


def get_docstring(function):
  if isinstance(function, (staticmethod, classmethod)):
    return function.__func__.__doc__ or ''
  elif hasattr(function, '__name__') or isinstance(function, property):
    return function.__doc__ or ''
  elif hasattr(function, '__call__'):
    return function.__call__.__doc__ or ''
  else:
    return function.__doc__ or ''


def get_full_arg_spec(func):
  if hasattr(inspect, 'getfullargspec'):
    spec = inspect.getfullargspec(func)
    return {k: getattr(spec, k) for k in dir(spec) if not k.startswith('_')}
  spec = inspect.getargspec(func)
  return {
    'args': spec.args,
    'varargs': spec.varargs,
    'varkw': spec.keywords,
    'defaults': spec.defaults,
    'kwonlyargs': [],
    'kwonlydefaults': [],
    'annotations': {}
  }


class Parameter(object):
  POS = 'POS'
  KWONLY = 'KWONLY'
  VARARGS_POS = 'VARARGS_POS'
  VARARGS_KW = 'VARARGS_KW'

  Value = collections.namedtuple('Value', 'value')

  def __init__(self, kind, name, annotation=None, default=None):
    self.kind = kind
    self.name = name
    self.annotation = annotation
    self.default = default

  def __repr__(self):
    return 'Parameter(kind={}, name={!r}, annotation={!r}, default={!r})'\
        .format(self.kind, self.name, self.annotation, self.default)

  def __str__(self):
    result = self.name
    if self.annotation:
      result += ': ' + repr(self.annotation.value)
    if self.default:
      result += ' = ' + repr(self.default.value)
    if self.kind == self.VARARGS_POS:
      result = '*' + result
    if self.kind == self.VARARGS_KW:
      result = '**' + result
    return result

  def replace(self, name=NotSet, annotation=NotSet,
              default=NotSet, kind=NotSet):
    return Parameter(
      self.kind if kind is NotSet else kind,
      self.name if name is NotSet else name,
      self.annotation if annotation is NotSet else annotation,
      self.default if default is NotSet else default)


def get_paramaters_from_arg_spec(argspec, strip_self=False):
  args = [Parameter(Parameter.POS, x) for x in argspec['args'][:]]
  if argspec['defaults']:
    offset = len(args) - len(argspec['defaults'])
    for i, default in enumerate(argspec['defaults']):
      args[i + offset] = args[i + offset].replace(default=Parameter.Value(default))

  if argspec['varargs']:
    args.append(Parameter(Parameter.VARARGS_POS, argspec['varargs']))

  for name in argspec['kwonlyargs']:
    args.append(Parameter(Parameter.KWONLY, name))

  if argspec['varkw']:
    args.append(Parameter(Parameter.VARARGS_KW, argspec['varkw']))

  if strip_self and args and args[0].name == 'self':
    args.pop(0)

  for i, param in enumerate(args):
    if param.name in argspec['annotations']:
      annotation = argspec['annotations'][param.name]
      args[i] = param.replace(annotation=Parameter.Value(annotation))

  return args


def format_parameters_list(parameters):
  found_kwonly = False
  result = []
  for param in parameters:
    if param.kind == Parameter.KWONLY and not found_kwonly:
      found_kwonly = True
      result.append('*')
    result.append(str(param))
  return ', '.join(result)


def get_function_signature(
  function,
  owner_class=None,
  show_module=False,
  pretty=True,
):
  # Get base name.
  name_parts = []
  if show_module:
    name_parts.append(function.__module__)
  if owner_class:
    name_parts.append(owner_class.__name__)
  if hasattr(function, '__name__'):
    name_parts.append(function.__name__)
  else:
    name_parts.append(type(function).__name__)
    name_parts.append('__call__')
    function = function.__call__
  name = '.'.join(name_parts)

  try:
    argspec = get_full_arg_spec(function)
  except TypeError:
    parameters = []
  else:
    parameters = get_paramaters_from_arg_spec(argspec, strip_self=owner_class)

  # Prettify annotations.
  class repr_str(str):
    def __repr__(self):
      return self
  def prettify(val):  # type: (Parameter.Value) -> Parameter.Value
    if isinstance(val.value, type):
      val = Parameter.Value(repr_str(val.value.__name__))
    return val
  for i, param in enumerate(parameters):
    if param.annotation:
      param = param.replace(annotation=prettify(param.annotation))
    if param.default:
      param = param.replace(default=prettify(param.default))
    parameters[i] = param

  if pretty:
    # Replace annotations and defaults with placeholders that are valid syntax.
    supplements = {}
    counter = [0]

    def _add_supplement(value):
      annotation_id = '_{}'.format(counter[0])
      annotation_id += '_' * (len(repr(value)) - len(annotation_id))
      supplements[annotation_id] = value
      counter[0] += 1
      return repr_str(annotation_id)

    for i, param in enumerate(parameters):
      if param.annotation:
        param = param.replace(
          annotation=Parameter.Value(_add_supplement(param.annotation.value)))
      if param.default:
        param = param.replace(
          default=Parameter.Value(_add_supplement(param.default.value)))
      parameters[i] = param

  # Use a placeholder in pretty mode as the generated *name* may also
  # sometimes not be valid syntax (eg. if it includes the class name).
  name_placeholder = '_PH_' + '_' * (len(name)-2)
  sig = (name_placeholder if pretty else name) + '(' + format_parameters_list(parameters) + ')'

  if pretty:
    sig, _ = FormatCode('def ' + sig + ': pass', style_config='pep8')
    sig = sig[4:].rpartition(':')[0]

    # Replace the annotation and default placeholders with the actual values.
    for placeholder, annotation in supplements.items():
      sig = sig.replace(placeholder, repr(annotation))

    # Replace the placeholder and fix indents.
    sig = sig.replace(name_placeholder, name)
    delta = len(name_placeholder) - len(name)
    lines = sig.split('\n')
    for i, line in enumerate(lines[1:], 1):
      indent = len(line) - len(line.lstrip()) - delta - 4  # 4 for "def "
      if indent <= 0 and line.strip() != ')':
        indent = 4
      lines[i] = ' ' * indent + line.lstrip()
    sig = '\n'.join(lines)

  return sig
