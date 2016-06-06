PyExecJS
========
[![Build Status](https://travis-ci.org/doloopwhile/PyExecJS.svg?branch=travis-ci)](https://travis-ci.org/doloopwhile/PyExecJS)

Run JavaScript code from Python.

PyExecJS is a porting of ExecJS from Ruby.
PyExecJS **automatically** picks the best runtime available to evaluate your JavaScript program.

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

# Supported runtimes

* [PyV8](http://code.google.com/p/pyv8/) - A python wrapper for Google V8 engine,
* [Node.js](http://nodejs.org/)
* Apple JavaScriptCore - Included with Mac OS X
* [Mozilla SpiderMonkey](http://www.mozilla.org/js/spidermonkey/)
* [Microsoft Windows Script Host](http://msdn.microsoft.com/en-us/library/9bbdkx3k.aspx) (JScript)
* [SlimerJS](http://slimerjs.org/)
* [PhantomJS](http://phantomjs.org/)
* [Nashorn](http://docs.oracle.com/javase/8/docs/technotes/guides/scripting/nashorn/intro.html#sthref16) - Included with Oracle Java 8

# Installation

    $ pip install PyExecJS

or

    $ easy_install PyExecJS

# Details

If `EXECJS_RUNTIME` environment variable is specified, PyExecJS pick the JavaScript runtime as a default:

    >>> execjs.get().name # this value is depends on your environment.
    >>> os.environ["EXECJS_RUNTIME"] = "Node"
    >>> execjs.get().name
    'Node.js (V8)'

You can choose JavaScript runtime by `execjs.get()`:

    >>> default = execjs.get() # the automatically picked runtime
    >>> default.eval("1 + 2")
    3
    >>> import execjs.runtime_names
    >>> jscript = execjs.get(execjs.runtime_names.JScript)
    >>> jscript.eval("1 + 2")
    3
    >>> import execjs.runtime_names
    >>> node = execjs.get(execjs.runtime_names.Node)
    >>> node.eval("1 + 2")
    3

The pros of PyExecJS is that you do not need take care of JavaScript environment.
Especially, it works in Windows environment without installing extra libraries.

One of cons of PyExecJS is performance. PyExecJS communicate JavaScript runtime by text and it is slow.
The other cons is that it does not fully support runtime specific features.

[PyV8](https://code.google.com/p/pyv8/) might be better choice for some use case.

# License

Copyright (c) 2016 Omoto Kenji.
Copyright (c) 2011 Sam Stephenson and Josh Peek. (As a author of ExecJS)

Released under the MIT license. See `LICENSE` for details.

# Changelog

## 1.4.1
- Fixed arguments of module-level functions.
- Fixed bug of execution with pipe.
- Fixed wrong excption is raised.

## 1.4.0
- Fixed required libraries.
- Fixed order of output of `--print-available-runtimes`.
- Execute some JavaScript runtime with pipe/stdin (without temporary file).

## 1.3.1
- Fixed `--print-available-runtimes` fails in Python 2.7.

## 1.3.0
- Added `cwd` argument.

## 1.2.0
- Supported Python 3.5
- Supported Nashorn(Java 8 JavaScript engine) as runtime
- Dropped support for Python 2.6 and 3.2

## 1.1.0
- Supported Python 3.4
- Supported SlimerJS as runtime
- Supported PhantomJS as runtime
- Fixed JScript runtime on Windows 8

## 1.0.5
- Supported Python 3.3
- Fixed file handle leaking
- Fixed issue with passenger-nginx-4.0

## 1.0.4
- Removed "import execjs" (it prevent execution of setup.py by Python 2.6)

## 1.0.3
- Javascript sources were embeded in __init__.py. 'which' command were reimplemented by pure python.

## 1.0.2
- Python 2.6.x was supported.

## 1.0.1
- Forgotten shell=True was added to Popen.

## 1.0.0
- First release.
