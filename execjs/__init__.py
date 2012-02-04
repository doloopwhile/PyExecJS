#!/usr/bin/env python3
#encoding:shift-jis
from __future__ import unicode_literals, division, with_statement
'''
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

import sys
import os
import os.path
import io
import platform
import tempfile
from subprocess import Popen, PIPE, STDOUT
import json

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
    
__all__ = """
    get register runtimes get_from_environment exec_ eval compile
    ExternalRuntime Context
    Error RuntimeError ProgramError RuntimeUnavailable
""".split()

class Error(Exception): pass
class RuntimeError(Error): pass
class ProgramError(Error): pass
class RuntimeUnavailable(RuntimeError): pass


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
        raise RuntimeUnavailable("{name} runtime is not defined".format(name=name))
    else:
        if not runtime.is_available():
            raise RuntimeUnavailable(
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
    
    raise RuntimeUnavailable("Could not find a JavaScript runtime. " +
          "See https://github.com/sstephenson/execjs for a list of available runtimes.")


def get_from_environment():
    '''
        Return the JavaScript runtime that is specified in EXECJS_RUNTIME environment variable.
        If EXECJS_RUNTIME environment variable is empty of invalid, return None.
    '''
    try:
        name = os.environ["EXECJS_RUNTIME"]
    except KeyError:
        return None
    if not name: #name is None or empty str
        return None
    return get(name)


def eval(source):
    return get().eval(source)


def exec_(source):
    return get().exec_(source)


def compile(source):
    return get().compile(source)


def _root():
    return os.path.abspath(os.path.dirname(__file__))

def _is_windows():
    return platform.system() == 'Windows'

def _json2_source():
    with io.open(os.path.join(_root(), 'support', 'json2.js')) as fp:
        return fp.read()

def _windows_which():
    return os.path.join(_root(), "support", "which.bat")


class ExternalRuntime:
    def __init__(self, name, command, runner_path, encoding='utf8'):
        self._name = name
        self._command = command
        self._runner_path = runner_path
        self._encoding = encoding
    
    def __str__(self):
        return "{class_name}({runtime_name})".format(
            class_name=type(self).__name__,
            runtime_name=self._name,
        )
    
    @property
    def name(self):
        return self._name
    
    def exec_(self, source):
        if not self.is_available():
            raise RuntimeUnabailable()
        return self.Context(self).exec_(source)
    
    def eval(self, source):
        if not self.is_available():
            raise RuntimeUnabailable()
        return self.Context(self).eval(source)

    def compile(self, source):
        if not self.is_available():
            raise RuntimeUnabailable()
        return self.Context(self, source)

    def is_available(self):
        return self._binary() is not None
    
    def _binary(self):
        """protected"""
        if not hasattr(self, "_binary_cache"):
            self._binary_cache = self._which(self._command)
        return self._binary_cache
        
    def _runner_source(self):
        """protected"""
        if getattr(self, '_runner_source_cache', None) is None:
            with io.open(self._runner_path, encoding='utf8') as fp:
                self._runner_source_cache = fp.read()
        return self._runner_source_cache
    
    def _execfile(self, filename):
        """protected"""
        cmd = self._binary() + [filename]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        stdoutdata, stderrdata = p.communicate()
        ret = p.wait()
        del p
        if ret == 0:
            return stdoutdata
        else:
            raise RuntimeError(stdoutdata)
    
    def _which(self, command):
        """protected"""
        if isinstance(command, str):
            command = [command]
        
        name = command[0]
        args = command[1:]
        
        if _is_windows():
            which_command = [_windows_which(), name]
        else:
            which_command = ["command", "-v", name]
        p = Popen(which_command, stdout=PIPE, stderr=PIPE, shell=True)
        stdoutdata, _ = p.communicate()
        stdoutdata = stdoutdata.decode(sys.getfilesystemencoding())
        path = stdoutdata.strip().split('\n')[0]
        if not path:
            return None
        return [path] + args


    class Context:
        def __init__(self, runtime, source=''):
            self._runtime = runtime
            self._source = source
        
        def eval(self, source, options={}):
            if not source.strip():
                data = "''"
            else:
                data = "'('+" + json.dumps(source, ensure_ascii=True) + "+')'"
            
            code = 'return eval({data})'.format(data=data)
            return self.exec_(code, options=options)
        
        def exec_(self, source, options = {}):
            if self._source:
                source = self._source + '\n' + source
            
            (fd, filename) = tempfile.mkstemp(prefix='execjs', suffix='.js')
            os.close(fd)
            try:
                with io.open(filename, "w+", encoding=self._runtime._encoding) as fp:
                    fp.write(self._compile(source))
                output = self._runtime._execfile(filename)
            finally:
                os.remove(filename)
            
            output = output.decode(self._runtime._encoding)
            output = output.replace("\r\n", "\n").replace("\r", "\n")
            return self._extract_result(output.split("\n")[-2])
        
        def call(self, identifier, *args):
            args = json.dumps(args)
            return self.eval("{identifier}.apply(this, {args})".format(identifier=identifier, args=args))
        
        def _compile(self, source):
            """protected"""
            runner_source = self._runtime._runner_source()
            runner_source = runner_source.replace('#{source}', source)
            
            if runner_source.find('#{encoded_source}') >= 0:
                encoded_source = json.dumps(
                    "(function(){ " +
                    encode_unicode_codepoints(source) +
                    " })()"
                )
                runner_source = runner_source.replace(
                    '#{encoded_source}', encoded_source)
            
            if runner_source.find('#{json2_source}') >= 0:
                runner_source = runner_source.replace('#{json2_source}', _json2_source())
            
            return runner_source
        
        def _extract_result(self, output_last_line):
            """protected"""
            if not output_last_line:
                status = value = None
            else:
                ret = json.loads(output_last_line)
                if len(ret) == 1:
                    ret = [ret[0], None]
                status, value = ret
                
            if status == "ok":
                return value
            elif value.startswith('SyntaxError:'):
                raise RuntimeError(value)
            else:
                raise ProgramError(value)


def encode_unicode_codepoints(str):
    r"""
    >>> encode_unicode_codepoints("a") == 'a'
    True
    >>> ascii = ''.join(chr(i) for i in range(0x80))
    >>> encode_unicode_codepoints(ascii) == ascii
    True
    >>> encode_unicode_codepoints('\u4e16\u754c') == '\\u4e16\\u754c'
    True
    """
    codepoint_format = '\\u{ord:04x}'.format
    def codepoint(ch):
        o = ord(ch)
        if o in range(0x80):
            return ch
        else:
            return codepoint_format(ord=o)
    return ''.join(map(codepoint, str))


class PyV8Runtime:
    def __init__(self):
        try:
            import PyV8
        except ImportError:
            self._is_available = False
        else:
            self._is_available = True
    
    @property
    def name(self):
        return "PyV8"
    
    def exec_(self, source):
        return self.Context(self).exec_(source)
    
    def eval(self, source):
        return self.Context(self).eval(source)

    def compile(self, source):
        return self.Context(self, source)

    def is_available(self):
        return self._is_available


    class Context:
        def __init__(self, runtime, source=""):
            self._source = source
        
        def exec_(self, source):
            source = '''\
            (function() {{
                {0};
                {1};
            }})()'''.format(
                encode_unicode_codepoints(self._source),
                encode_unicode_codepoints(source)
            )
            source = str(source)
            
            import PyV8
            import contextlib
            #backward compatibility
            with contextlib.nested(PyV8.JSContext(), PyV8.JSEngine()) as (ctxt, engine):
                try:
                    script = engine.compile(source)
                except PyV8.JSError as e:
                    raise RuntimeError(e)
                try:
                    value = script.run()
                except PyV8.JSError as e:
                    raise ProgramError(e)
                return self.convert(value)
            
        def eval(self, source):
            return self.exec_('return ' + encode_unicode_codepoints(source))
            
        def call(self, identifier, *args):
            args = json.dumps(args)
            return self.eval("{identifier}.apply(this, {args})".format(identifier=identifier, args=args))
        
        @classmethod
        def convert(cls, obj):
            from PyV8 import _PyV8
            if isinstance(obj, bytes):
                return obj.decode('utf8')
            if isinstance(obj, _PyV8.JSArray):
                return [cls.convert(v) for v in obj]
            elif isinstance(obj, _PyV8.JSFunction):
                return None
            elif isinstance(obj, _PyV8.JSObject):
                ret = {}
                for k in obj.keys():
                    v = cls.convert(obj[k])
                    if v is not None:
                        ret[cls.convert(k)] = v
                return ret
            else:
                return obj


_runtimes = OrderedDict()
_runtimes['PyV8'] = PyV8Runtime()

for command in ["nodejs", "node"]:
    _runtimes["Node"] = runtime = ExternalRuntime(
        name = "Node.js (V8)",
        command = [command],
        runner_path = os.path.join(_root(), "support", "node_runner.js"),
        encoding='UTF-8',
    )
    if runtime.is_available():
        break

del command
del runtime

_runtimes['JavaScriptCore'] = ExternalRuntime(
    name        = "JavaScriptCore",
    command     = ["/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc"],
    runner_path = os.path.join(_root(), "support", "jsc_runner.js")
)


_runtimes['SpiderMonkey'] = _runtimes['Spidermonkey'] = ExternalRuntime(
    name        = "SpiderMonkey",
    command     = ["js"],
    runner_path = os.path.join(_root(), "support", "spidermonkey_runner.js")
)


_runtimes['JScript'] = ExternalRuntime(
    name        = "JScript",
    command     = ["cscript", "//E:jscript", "//Nologo", "//U"],
    runner_path = os.path.join(_root(), "support", "jscript_runner.js"),
    encoding    = 'UTF-16LE' # CScript with //U returns UTF-16LE
)


