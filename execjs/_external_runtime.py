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
    def __init__(self, name, command, runner_source, encoding='utf8', tempfile=False):
        self._name = name
        if isinstance(command, str):
            command = [command]
        self._command = command
        self._runner_source = runner_source
        self._encoding = encoding
        self._tempfile = tempfile

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
        return self.Context(self, source, cwd=cwd, tempfile=tempfile)

    def _binary(self):
        if not hasattr(self, "_binary_cache"):
            self._binary_cache = _which(self._command)
        return self._binary_cache

    class Context(AbstractRuntimeContext):
        # protected

        def __init__(self, runtime, source='', cwd=None, tempfile=False):
            self._runtime = runtime
            self._source = source
            self._cwd = cwd
            self._tempfile = tempfile

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

            if self._tempfile:
                output = self._exec_with_tempfile(source)
            else:
                output = self._exec_with_pipe(source)
            return self._extract_result(output)

        def _call(self, identifier, *args):
            args = json.dumps(args)
            return self._eval("{identifier}.apply(this, {args})".format(identifier=identifier, args=args))

        def _exec_with_pipe(self, source):
            cmd = self._runtime._binary()

            p = None
            try:
                p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=self._cwd, universal_newlines=True)
                stdoutdata, stderrdata = p.communicate(input=source)
                ret = p.wait()
            finally:
                del p

            self._fail_on_non_zero_status(ret, stdoutdata, stderrdata)
            return stdoutdata

        def _exec_with_tempfile(self, source):
            (fd, filename) = tempfile.mkstemp(prefix='execjs', suffix='.js')
            os.close(fd)
            try:
                with io.open(filename, "w+", encoding=self._runtime._encoding) as fp:
                    fp.write(self._compile(source))
                cmd = self._runtime._binary() + [filename]

                p = None
                try:
                    p = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=self._cwd)
                    stdoutdata, stderrdata = p.communicate()
                    ret = p.wait()
                finally:
                    del p

                self._fail_on_non_zero_status(ret, stdoutdata, stderrdata)
                return stdoutdata
            finally:
                os.remove(filename)

        def _fail_on_non_zero_status(self, status, stdoutdata, stderrdata):
            if status != 0:
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


def node():
    r = node_node()
    if r.is_available():
        return r
    return node_nodejs()


def node_node():
    return ExternalRuntime(
        name="Node.js (V8)",
        command=['node'],
        encoding='UTF-8',
        runner_source=_runner_sources.Node
    )


def node_nodejs():
    return ExternalRuntime(
        name="Node.js (V8)",
        command=['nodejs'],
        encoding='UTF-8',
        runner_source=_runner_sources.Node
    )


def jsc():
    return ExternalRuntime(
        name="JavaScriptCore",
        command=["/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc"],
        runner_source=_runner_sources.JavaScriptCore
    )


def spidermonkey():
    return ExternalRuntime(
        name="SpiderMonkey",
        command=["js"],
        runner_source=_runner_sources.SpiderMonkey
    )


def jscript():
    return ExternalRuntime(
        name="JScript",
        command=["cscript", "//E:jscript", "//Nologo"],
        encoding="ascii",
        runner_source=_runner_sources.JScript,
        tempfile=True
    )


def phantomjs():
    return ExternalRuntime(
        name="PhantomJS",
        command=["phantomjs"],
        runner_source=_runner_sources.PhantomJS
    )


def slimerjs():
    return ExternalRuntime(
        name="SlimerJS",
        command=["slimerjs"],
        runner_source=_runner_sources.SlimerJS
    )


def nashorn():
    return ExternalRuntime(
        name="Nashorn",
        command=["jjs"],
        runner_source=_runner_sources.Nashorn
    )
