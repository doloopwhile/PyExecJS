from subprocess import Popen, PIPE
import io
import json
import os
import os.path
import platform
import re
import stat
import sys
import tempfile
import six
import execjs._json2 as _json2
import execjs._runner_sources as _runner_sources
import execjs._exceptions as exceptions
from execjs._abstract_runtime import AbstractRuntime
from execjs._abstract_runtime_context import AbstractRuntimeContext
from execjs._misc import encode_unicode_codepoints


class ExternalRuntime(AbstractRuntime):
    '''Runtime to execute codes with external command.'''
    def __init__(self, name, command, runner_source, encoding='utf8'):
        self._name = name
        if isinstance(command, str):
            command = [command]
        self._command = command
        self._runner_source = runner_source
        self._encoding = encoding

        self._available = self._binary() is not None

    def __str__(self):
        return "{class_name}({runtime_name})".format(
            class_name=type(self).__name__,
            runtime_name=self._name,
        )

    @property
    def name(self):
        return self._name

    def is_available(self):
        return self._available

    def _compile(self, source, cwd=None):
        return self.Context(self, source, cwd=cwd)

    def _binary(self):
        if not hasattr(self, "_binary_cache"):
            self._binary_cache = _which(self._command)
        return self._binary_cache

    class Context(AbstractRuntimeContext):
        # protected

        def __init__(self, runtime, source='', cwd=None):
            self._runtime = runtime
            self._source = source
            self._cwd = cwd

        def is_available(self):
            return self._runtime.is_available()

        def _eval(self, source):
            if not source.strip():
                data = "''"
            else:
                data = "'('+" + json.dumps(source, ensure_ascii=True) + "+')'"

            code = 'return eval({data})'.format(data=data)
            return self.exec_(code)

        def _exec_(self, source):
            if self._source:
                source = self._source + '\n' + source

            (fd, filename) = tempfile.mkstemp(prefix='execjs', suffix='.js')
            os.close(fd)
            try:
                with io.open(filename, "w+", encoding=self._runtime._encoding) as fp:
                    fp.write(self._compile(source))
                output = self._execfile(filename)
            finally:
                os.remove(filename)

            return self._extract_result(output)

        def _call(self, identifier, *args):
            args = json.dumps(args)
            return self.eval("{identifier}.apply(this, {args})".format(identifier=identifier, args=args))

        def _execfile(self, filename):
            cmd = self._runtime._binary() + [filename]

            p = None
            try:
                p = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=self._cwd)
                stdoutdata, stderrdata = p.communicate()
                ret = p.wait()
            finally:
                del p

            if ret == 0:
                return stdoutdata
            else:
                raise exceptions.RuntimeError("stdout: {}, stderr: {}".format(repr(stdoutdata), repr(stderrdata)))

        def _compile(self, source):
            runner_source = self._runtime._runner_source

            replacements = {
                '#{source}': lambda: source,
                '#{encoded_source}': lambda: json.dumps(
                    "(function(){ " +
                    encode_unicode_codepoints(source) +
                    " })()"
                ),
                '#{json2_source}': _json2._json2_source,
            }

            pattern = "|".join(re.escape(k) for k in replacements)

            runner_source = re.sub(pattern, lambda m: replacements[m.group(0)](), runner_source)

            return runner_source

        def _extract_result(self, output):
            output = output.decode(self._runtime._encoding)
            output = output.replace("\r\n", "\n").replace("\r", "\n")
            output_last_line = output.split("\n")[-2]

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
                raise exceptions.RuntimeError(value)
            else:
                raise exceptions.ProgramError(value)


def _is_windows():
    """protected"""
    return platform.system() == 'Windows'


def _decode_if_not_text(s):
    """protected"""
    if isinstance(s, six.text_type):
        return s
    return s.decode(sys.getfilesystemencoding())


def _find_executable(prog, pathext=("",)):
    """protected"""
    pathlist = _decode_if_not_text(os.environ.get('PATH', '')).split(os.pathsep)

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
    """protected"""
    if isinstance(command, str):
        command = [command]
    command = list(command)
    name = command[0]
    args = command[1:]

    if _is_windows():
        pathext = _decode_if_not_text(os.environ.get("PATHEXT", ""))
        path = _find_executable(name, pathext.split(os.pathsep))
    else:
        path = _find_executable(name)

    if not path:
        return None
    return [path] + args


node = ExternalRuntime(name="Node.js (V8)", command=['node'], encoding='UTF-8', runner_source=_runner_sources.Node)
nodejs = ExternalRuntime(name="Node.js (V8)", command=['nodejs'], encoding='UTF-8', runner_source=_runner_sources.Node)

jsc = ExternalRuntime(
    name="JavaScriptCore",
    command=["/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc"],
    runner_source=_runner_sources.JavaScriptCore
)

spidermonkey = ExternalRuntime(name="SpiderMonkey", command=["js"], runner_source=_runner_sources.SpiderMonkey)

jscript = ExternalRuntime(
    name="JScript",
    command=["cscript", "//E:jscript", "//Nologo"],
    encoding="ascii",
    runner_source=_runner_sources.JScript
)

phantomjs = ExternalRuntime(name="PhantomJS", command=["phantomjs"], runner_source=_runner_sources.PhantomJS)
slimerjs = ExternalRuntime(name="SlimerJS", command=["slimerjs"], runner_source=_runner_sources.SlimerJS)
nashorn = ExternalRuntime(name="Nashorn", command=["jjs"], runner_source=_runner_sources.Nashorn)
