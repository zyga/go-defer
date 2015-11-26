"""
Go's defer for python.

The idea behind defer is very simple. Defer postpones a call to a function till
the end of the enclosing function call.

Defer calls are pushed to a stack and called in LIFO (last-in-first-out) order.

Example::

    >>> @with_defer
    ... def foo():
    ...     for i in range(4):
    ...         defer(print, i)
    >>> foo()
    3
    2
    1
    0
"""

from __future__ import print_function, absolute_import

import functools
import inspect
import logging

__all__ = ('defer', 'with_defer')


class _defer_chain(object):

    def __init__(self):
        self._chain = []

    def defer(self, fn, args, kwargs, filename, lineno):
        self._chain.append((fn, args, kwargs, filename, lineno))

    def cleanup(self):
        if self._chain is None:
            return
        for fn, args, kwargs, filename, lineno in reversed(self._chain):
            try:
                fn(*args, **kwargs)
            except Exception as exc:
                logging.error(
                    "defer call in %s:%d raised: %s", filename, lineno, exc)
        self._chain = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()


def with_defer(fn):
    """
    Decorator for functions that use defer()

    :param fn:
        Function to decorate
    :returns:
        Decorated function that can now use defer()
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with _defer_chain() as __defer__:
            __defer__  # Just to seem used
            return fn(*args, **kwargs)
    return wrapper


def defer(fn, *args, **kwargs):
    """
    Defer the call to fn(...) until the end of the function scope.

    :param fn:
        The function to call
    :param args:
        Positional arguments to pass to the function
    :param kwargs:
        Keyword arguments to pass to the function
    """
    with_defer_f = inspect.stack(context=0)[2][0]
    caller_f = inspect.stack(context=0)[1][0]
    try:
        if '__defer__' not in with_defer_f.f_locals:
            raise TypeError("decorate {} with @defer.with_defer".format(
                with_defer_f.f_code.co_name))
        with_defer_f.f_locals['__defer__'].defer(
            fn, args, kwargs, caller_f.f_code.co_filename, caller_f.f_lineno)
    finally:
        del with_defer_f
        del caller_f
