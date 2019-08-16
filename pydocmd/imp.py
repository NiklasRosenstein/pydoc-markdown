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
This module provides utilities for importing Python objects by name.
"""

import types
import inspect


def import_module(name):
    """
    Imports a Python module assuming that the whole *name* identifies only a
    Python module and no symbol inside a Python module.
    """

    # fromlist must not be empty so we get the bottom-level module rather than
    # the top-level module.
    return __import__(name, fromlist=[''])


def import_object(name):
    """
    Like #import_object_with_scope() but returns only the object.
    """

    return import_object_with_scope(name)[0]


def import_object_with_scope(name):
    """
    Imports a Python object by an absolute identifier.

    # Arguments
    name (str): The name of the Python object to import.

    # Returns
    (any, Module): The object and the module that contains it. Note that
      for plain modules loaded with this function, both elements of the
      tuple may be the same object.
    """

    # Import modules until we can no longer import them. Prefer existing
    # attributes over importing modules at each step.
    parts = name.split('.')
    current_name = parts[0]
    obj = import_module(current_name)
    scope = None
    for part in parts[1:]:
        current_name += '.' + part
        try:
            if hasattr(obj, '__dict__'):
                # Using directly __dict__ for descriptors, where we want to get the descriptor's instance
                # and not calling the descriptor's __get__ method.
                sub_obj = obj.__dict__[part]
            else:
                sub_obj = getattr(obj, part)

            scope, obj = obj, sub_obj
        except (AttributeError, KeyError):
            try:
                obj = scope = import_module(current_name)
            except ImportError as exc:
                if 'named {}'.format(part) in str(exc):
                    raise ImportError(current_name)
                raise
    return obj, scope


def force_lazy_import(name):
    """
    Import any modules off of "name" by iterating a new list rather than a generator so that this
    library works with lazy imports.
    """
    obj = import_object(name)
    module_items = list(getattr(obj, '__dict__', {}).items())
    for key, value in module_items:
        if getattr(value, '__module__', None):
            import_object(name + '.' + key)


def dir_object(name, sort_order, need_docstrings=True):
    prefix = None
    obj = import_object(name)
    if isinstance(obj, types.ModuleType):
        prefix = obj.__name__
    all = getattr(obj, '__all__', None)

    # Import any modules attached to this object so that this will work with lazy imports.  Otherwise
    # the block below will fail because the object will change while it's being iterated.
    force_lazy_import(name)

    by_name = []
    by_lineno = []
    for key, value in getattr(obj, '__dict__', {}).items():
        if isinstance(value, (staticmethod, classmethod)):
            value = value.__func__
        if key.startswith('_'):
            continue
        if not hasattr(value, '__doc__'):
            continue

        # If we have a type, we only want to skip it if it doesn't have
        # any documented members.
        if not (isinstance(value, type) and dir_object(name + '.' + key, sort_order, True)):
            if need_docstrings and not value.__doc__:
                continue
            if all is not None and key not in all:
                continue

        if prefix is not None and getattr(value, '__module__', None) != prefix:
            continue
        if sort_order == 'line':
            try:
                by_lineno.append((key, inspect.getsourcelines(value)[1]))
            except Exception:
                # some members don't have (retrievable) line numbers (e.g., properties)
                # so fall back to sorting those first, and by name
                by_name.append(key)
        else:
            by_name.append(key)
    by_name = sorted(by_name, key=lambda s: s.lower())
    by_lineno = [key for key, lineno in sorted(by_lineno, key=lambda r: r[1])]

    return by_name + by_lineno
