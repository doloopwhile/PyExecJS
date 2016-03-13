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

import execjs._runtimes
import execjs._external_runtime as external_runtime
ExternalRuntime = external_runtime.ExternalRuntime


__all__ = """
    get register runtimes get_from_environment exec_ eval compile
    ExternalRuntime
    Error RuntimeError ProgramError RuntimeUnavailableError
""".split()


class Error(Exception):
    pass


class RuntimeError(Error):
    pass


class ProgramError(Error):
    pass


class RuntimeUnavailableError(RuntimeError):
    pass


register = execjs._runtimes.register
get = execjs._runtimes.get
runtimes = execjs._runtimes.runtimes
available_runtimes = execjs._runtimes.available_runtimes
get_from_environment = execjs._runtimes.get_from_environment


def eval(source):
    return get().eval(source)


def exec_(source):
    return get().exec_(source)


def compile(source):
    return get().compile(source)
