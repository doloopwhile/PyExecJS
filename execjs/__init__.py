#!python3
#encoding: ascii
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
import stat
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
    
    raise RuntimeUnavailable("Could not find a JavaScript runtime.")


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
    # The folowing code is json2.js(https://github.com/douglascrockford/JSON-js).
    # It is compressed by YUI Compressor Online(http://yui.2clics.net/).
    
    return 'var JSON;if(!JSON){JSON={}}(function(){function f(n){return n<10?"0"+n:n}if(typeof Date.prototype.toJSON!=="function"){Date.prototype.toJSON=function(key){return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z":null};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(key){return this.valueOf()}}var cx=/[\\u0000\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/g,escapable=/[\\\\\\"\\x00-\\x1f\\x7f-\\x9f\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/g,gap,indent,meta={"\\b":"\\\\b","\\t":"\\\\t","\\n":"\\\\n","\\f":"\\\\f","\\r":"\\\\r",\'"\':\'\\\\"\',"\\\\":"\\\\\\\\"},rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?\'"\'+string.replace(escapable,function(a){var c=meta[a];return typeof c==="string"?c:"\\\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+\'"\':\'"\'+string+\'"\'}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==="object"&&typeof value.toJSON==="function"){value=value.toJSON(key)}if(typeof rep==="function"){value=rep.call(holder,key,value)}switch(typeof value){case"string":return quote(value);case"number":return isFinite(value)?String(value):"null";case"boolean":case"null":return String(value);case"object":if(!value){return"null"}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==="[object Array]"){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||"null"}v=partial.length===0?"[]":gap?"[\\n"+gap+partial.join(",\\n"+gap)+"\\n"+mind+"]":"["+partial.join(",")+"]";gap=mind;return v}if(rep&&typeof rep==="object"){length=rep.length;for(i=0;i<length;i+=1){if(typeof rep[i]==="string"){k=rep[i];v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}else{for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}v=partial.length===0?"{}":gap?"{\\n"+gap+partial.join(",\\n"+gap)+"\\n"+mind+"}":"{"+partial.join(",")+"}";gap=mind;return v}}if(typeof JSON.stringify!=="function"){JSON.stringify=function(value,replacer,space){var i;gap="";indent="";if(typeof space==="number"){for(i=0;i<space;i+=1){indent+=" "}}else{if(typeof space==="string"){indent=space}}rep=replacer;if(replacer&&typeof replacer!=="function"&&(typeof replacer!=="object"||typeof replacer.length!=="number")){throw new Error("JSON.stringify")}return str("",{"":value})}}if(typeof JSON.parse!=="function"){JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==="object"){for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v}else{delete value[k]}}}}return reviver.call(holder,key,value)}text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return"\\\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})}if(/^[\\],:{}\\s]*$/.test(text.replace(/\\\\(?:["\\\\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\\\\n\\r]*"|true|false|null|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?/g,"]").replace(/(?:^|:|,)(?:\\s*\\[)+/g,""))){j=eval("("+text+")");return typeof reviver==="function"?walk({"":j},""):j}throw new SyntaxError("JSON.parse")}}}());'


def _find_executable(prog, pathext=("",)):
    pathlist = os.environ['PATH'].split(os.pathsep)
    
    for dir in pathlist:
        for ext in pathext:
            filename = os.path.join(dir, prog + ext)
            try:
                st = os.stat(filename)
            except os.error:
                continue
            if stat.S_ISREG(st.st_mode) and (stat.S_IMODE(st.st_mode) & 0o111):
                return filename
    return None


def _which(command):
    if isinstance(command, str):
        command = [command]
    command = list(command)
    name = command[0]
    args = command[1:]
    
    if _is_windows():
        path = _find_executable(name, os.environ["PATHEXT"].split(os.pathsep))
    else:
        path = _find_executable(name)
        
    if not path:
        return None
    return [path] + args


class ExternalRuntime:
    def __init__(self, name, command, runner_source, encoding='utf8'):
        self._name = name
        if isinstance(command, str):
            command = [command]
        self._command = command
        self._runner_source = runner_source
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
            raise RuntimeUnavailable()
        return self.Context(self).exec_(source)
    
    def eval(self, source):
        if not self.is_available():
            raise RuntimeUnavailable()
        return self.Context(self).eval(source)

    def compile(self, source):
        if not self.is_available():
            raise RuntimeUnavailable()
        return self.Context(self, source)

    def is_available(self):
        return self._binary() is not None
    
    def runner_source(self):
        return self._runner_source
        
    def _binary(self):
        """protected"""
        if not hasattr(self, "_binary_cache"):
            self._binary_cache = _which(self._command)
        return self._binary_cache
    
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
            runner_source = self._runtime.runner_source().replace('#{source}', source)
            
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
        encoding='UTF-8',
        runner_source = r"""(function(program, execJS) { execJS(program) })(function() { #{source}
}, function(program) {
  var output;
  var print = function(string) {
    process.stdout.write('' + string + '\n');
  };
  try {
    result = program();
    print('')
    if (typeof result == 'undefined' && result !== null) {
      print('["ok"]');
    } else {
      try {
        print(JSON.stringify(['ok', result]));
      } catch (err) {
        print('["err"]');
      }
    }
  } catch (err) {
    print(JSON.stringify(['err', '' + err]));
  }
});""",
    )
    if runtime.is_available():
        break

del command
del runtime

_runtimes['JavaScriptCore'] = ExternalRuntime(
    name        = "JavaScriptCore",
    command     = ["/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc"],
    runner_source = r"""(function(program, execJS) { execJS(program) })(function() {
  return eval(#{encoded_source});
}, function(program) {
  var output;
  try {
    result = program();
    print("");
    if (typeof result == 'undefined' && result !== null) {
      print('["ok"]');
    } else {
      try {
        print(JSON.stringify(['ok', result]));
      } catch (err) {
        print('["err"]');
      }
    }
  } catch (err) {
    print(JSON.stringify(['err', '' + err]));
  }
});
"""
)


_runtimes['SpiderMonkey'] = _runtimes['Spidermonkey'] = ExternalRuntime(
    name        = "SpiderMonkey",
    command     = ["js"],
    runner_source = r"""(function(program, execJS) { execJS(program) })(function() { #{source}
}, function(program) {
  #{json2_source}
  var output;
  try {
    result = program();
    print("");
    if (typeof result == 'undefined' && result !== null) {
      print('["ok"]');
    } else {
      try {
        print(JSON.stringify(['ok', result]));
      } catch (err) {
        print('["err"]');
      }
    }
  } catch (err) {
    print(JSON.stringify(['err', '' + err]));
  }
});
""")


_runtimes['JScript'] = ExternalRuntime(
    name        = "JScript",
    command     = ["cscript", "//E:jscript", "//Nologo", "//U"],
    encoding    = 'UTF-16LE', # CScript with //U returns UTF-16LE
    runner_source = r"""(function(program, execJS) { execJS(program) })(function() {
  return eval(#{encoded_source});
}, function(program) {
  #{json2_source}
  var output, print = function(string) {
    WScript.Echo(string);
  };
  try {
    result = program();
    print("")
    if (typeof result == 'undefined' && result !== null) {
      print('["ok"]');
    } else {
      try {
        print(JSON.stringify(['ok', result]));
      } catch (err) {
        print('["err"]');
      }
    }
  } catch (err) {
    print(JSON.stringify(['err', err.name + ': ' + err.message]));
  }
});
"""
)


