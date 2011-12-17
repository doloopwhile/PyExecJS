PyExecJS
========
Run JavaScript code from Python.

PyExecJS is a porting of ExecJS from Ruby.
PyExecJS automatically picks the best runtime available to evaluate your JavaScript program,
then returns the result to you as a Python object.

A short example:

    >>> execjs.eval("'red yellow blue'.split(' ')")
    ['red', 'yellow', 'blue']
    >>> ctx = execjs.compile("""
    ...     function add(x, y) {
    ...         return x + y;
    ...     }
    ... """)
    >>> ctx.call("add", 1, 2)
    3

PyExecJS supports these runtimes:

* [PyV8](http://code.google.com/p/pyv8/) - A python wrapper for Google V8 engine, 
* [Node.js](http://nodejs.org/)
* Apple JavaScriptCore - Included with Mac OS X
* [Mozilla SpiderMonkey](http://www.mozilla.org/js/spidermonkey/)
* [Microsoft Windows Script Host](http://msdn.microsoft.com/en-us/library/9bbdkx3k.aspx) (JScript)


# Installation

    $ pip install execjs

or
    
    $ easy_install execjs


# License

Copyright (c) 2011 Omoto Kenji.
Copyright (c) 2011 Sam Stephenson and Josh Peek.

Released under the MIT license. See `LICENSE` for details.
