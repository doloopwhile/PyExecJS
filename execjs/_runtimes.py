import os.path
from collections import OrderedDict

import execjs.runtime_names as runtime_names
import execjs._external_runtime as external_runtime
import execjs._pyv8runtime as pyv8runtime
import execjs._exceptions as exceptions


def register(name, runtime):
    '''Register a JavaScript runtime.'''
    _runtimes.append((name, runtime))


def get(name=None):
    """
    Return a appropriate JavaScript runtime.
    If name is specified, return the runtime.
    """
    if name is None:
        return get_from_environment() or _find_available_runtime()
    return _find_runtime_by_name(name)


def runtimes():
    """return a dictionary of all supported JavaScript runtimes."""
    return OrderedDict(_runtimes)


def get_from_environment():
    '''
        Return the JavaScript runtime that is specified in EXECJS_RUNTIME environment variable.
        If EXECJS_RUNTIME environment variable is empty or invalid, return None.
    '''
    name = os.environ.get("EXECJS_RUNTIME", "")
    if not name:
        return None

    try:
        return _find_runtime_by_name(name)
    except exceptions.RuntimeUnavailableError:
        return None


def _find_available_runtime():
    for _, runtime in _runtimes:
        if runtime.is_available():
            return runtime
    raise exceptions.RuntimeUnavailableError("Could not find an available JavaScript runtime.")


def _find_runtime_by_name(name):
    for runtime_name, runtime in _runtimes:
        if runtime_name.lower() == name.lower():
            break
    else:
        raise exceptions.RuntimeUnavailableError("{name} runtime is not defined".format(name=name))

    if not runtime.is_available():
        raise exceptions.RuntimeUnavailableError(
            "{name} runtime is not available on this system".format(name=runtime.name))
    return runtime


_runtimes = []

register(runtime_names.PyV8,           pyv8runtime.PyV8Runtime())
register(runtime_names.Node,           external_runtime.node())
register(runtime_names.JavaScriptCore, external_runtime.jsc())
register(runtime_names.SpiderMonkey,   external_runtime.spidermonkey())
register(runtime_names.JScript,        external_runtime.jscript())
register(runtime_names.PhantomJS,      external_runtime.phantomjs())
register(runtime_names.SlimerJS,       external_runtime.slimerjs())
register(runtime_names.Nashorn,        external_runtime.nashorn())
