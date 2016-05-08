#!/usr/bin/env python3
# -*- coding: ascii -*-
'''r
Run JavaScript code from Python.

PyExecJS is a porting of ExecJS from Ruby.
PyExecJS automatically picks the best runtime available to evaluate your JavaScript program,
then returns the result to you as a Python object.

A short example:

>>> import execjs
>>> execjs.eval("'red yellow blue'.split(' ')")
['red', 'yellow', 'blue']
>>> ctx = execjs.compile("""
...     function add(x, y) {
...         return x + y;
...     }
... """)
>>> ctx.call("add", 1, 2)
3
'''
from __future__ import unicode_literals, division, with_statement

from execjs._exceptions import Error, RuntimeError, ProgramError, RuntimeUnavailableError
import execjs._runtimes
from execjs._external_runtime import ExternalRuntime
from execjs._abstract_runtime import AbstractRuntime


__all__ = """
    get register runtimes get_from_environment exec_ eval compile
    ExternalRuntime
    Error RuntimeError ProgramError RuntimeUnavailableError
""".split()


register = execjs._runtimes.register
get = execjs._runtimes.get
runtimes = execjs._runtimes.runtimes
get_from_environment = execjs._runtimes.get_from_environment


def eval(source):
    return get().eval(source)
eval.__doc__= AbstractRuntime.eval.__doc__


def exec_(source):
    return get().exec_(source)
exec_.__doc__= AbstractRuntime.exec_.__doc__


def compile(source):
    return get().compile(source)
compile.__doc__= AbstractRuntime.compile.__doc__
