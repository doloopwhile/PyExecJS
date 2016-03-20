import os.path

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import execjs._external_runtime as external_runtime
import execjs._pyv8runtime as pyv8runtime
import execjs._exceptions as exceptions


def register(name, runtime):
    '''Register a JavaScript runtime.'''
    _runtimes[name] = runtime


def get(name=None):
    """
    Return a appropriate JavaScript runtime.
    If name is specified, return the runtime.
    """
    if name is None:
        return _auto_detect()

    try:
        runtime = runtimes()[name]
    except KeyError:
        raise exceptions.RuntimeUnavailableError("{name} runtime is not defined".format(name=name))
    else:
        if not runtime.is_available():
            raise exceptions.RuntimeUnavailableError(
                "{name} runtime is not available on this system".format(name=runtime.name))
        return runtime


def runtimes():
    """return a dictionary of all supported JavaScript runtimes."""
    return dict(_runtimes)


def available_runtimes():
    """return a dictionary of all supported JavaScript runtimes which is usable"""
    return dict((name, runtime) for name, runtime in _runtimes.items() if runtime.is_available())


def _auto_detect():
    runtime = get_from_environment()
    if runtime is not None:
        return runtime

    for runtime in _runtimes.values():
        if runtime.is_available():
            return runtime

    raise exceptions.RuntimeUnavailableError("Could not find a JavaScript runtime.")


def get_from_environment():
    '''
        Return the JavaScript runtime that is specified in EXECJS_RUNTIME environment variable.
        If EXECJS_RUNTIME environment variable is empty or invalid, return None.
    '''
    try:
        name = os.environ["EXECJS_RUNTIME"]
    except KeyError:
        return None

    if not name:
        return None
    return get(name)


_runtimes = OrderedDict()

register('PyV8', pyv8runtime.PyV8Runtime())

if external_runtime.node.is_available():
    register("Node", external_runtime.node)
else:
    register("Node", external_runtime.nodejs)

register('JavaScriptCore', external_runtime.jsc)
register('SpiderMonkey', external_runtime.spidermonkey)
register('Spidermonkey', external_runtime.spidermonkey)
register('JScript', external_runtime.jscript)
register("PhantomJS", external_runtime.phantomjs)
register("SlimerJS", external_runtime.slimerjs)
register('Nashorn', external_runtime.nashorn)
