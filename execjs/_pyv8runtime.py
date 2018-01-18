import json

import execjs._exceptions as exceptions
from execjs._abstract_runtime import AbstractRuntime
from execjs._abstract_runtime_context import AbstractRuntimeContext
from execjs._misc import encode_unicode_codepoints

try:
    import PyV8
except ImportError:
    _pyv8_available = False
else:
    _pyv8_available = True


class PyV8Runtime(AbstractRuntime):
    '''Runtime to execute codes with PyV8.'''
    def __init__(self):
        pass

    @property
    def name(self):
        return "PyV8"

    def _compile(self, source, cwd=None):
        return self.Context(source)

    def is_available(self):
        return _pyv8_available

    class Context(AbstractRuntimeContext):
        def __init__(self, source=""):
            self._source = source

        def is_available(self):
            return _pyv8_available

        def _exec_(self, source):
            source = '''\
            (function() {{
                {0};
                {1};
            }})()'''.format(
                encode_unicode_codepoints(self._source),
                encode_unicode_codepoints(source)
            )
            source = str(source)

            # backward compatibility
            with PyV8.JSContext() as ctxt, PyV8.JSEngine() as engine:
                js_errors = (PyV8.JSError, IndexError, ReferenceError, SyntaxError, TypeError)
                try:
                    script = engine.compile(source)
                except js_errors as e:
                    raise exceptions.ProgramError(e)
                try:
                    value = script.run()
                except js_errors as e:
                    raise exceptions.ProgramError(e)
                return self.convert(value)

        def _eval(self, source):
            return self.exec_('return ' + encode_unicode_codepoints(source))

        def _call(self, identifier, *args):
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
