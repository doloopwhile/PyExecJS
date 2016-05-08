#!/usr/bin/env python3
# -*- coding: ascii -*-
from __future__ import unicode_literals
import sys
import io
from argparse import ArgumentParser, Action, SUPPRESS

import execjs


class PrintRuntimes(Action):
    def __init__(self, option_strings, dest=SUPPRESS, default=SUPPRESS, help=None):
        super(PrintRuntimes, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        message = "".join(name + "\n" for name, runtime in execjs.runtimes().items() if runtime.is_available())
        parser.exit(message=message)


def main():
    parser = ArgumentParser()
    parser.add_argument('--print-available-runtimes', action=PrintRuntimes)
    parser.add_argument('-r', '--runtime', action='store', dest='runtime')
    parser.add_argument('-e', '--eval', action='store', dest='expr')
    parser.add_argument("--encoding", action="store", dest="files_encoding", default="utf8")
    parser.add_argument(nargs="*", action='store', dest='files')

    opts = parser.parse_args()

    runtime = execjs.get(opts.runtime)

    codes = []
    for f in opts.files:
        with io.open(f, encoding=opts.files_encoding) as fp:
            codes.append(fp.read())

    context = runtime.compile("\n".join(codes))
    if opts.expr:
        if isinstance(opts.expr, bytes):
            expr = opts.expr.decode()
        else:
            expr = opts.expr
        sys.stdout.write(repr(context.eval(expr)) + "\n")
    else:
        ret = context.eval(sys.stdin.read())
        sys.stdout.write(repr(ret) + "\n")

if "__main__" == __name__:
    main()
