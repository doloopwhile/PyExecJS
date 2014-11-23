#!/bin/bash
cat README.md \
  | grep -v -F '![Build Status]' \
  | pandoc -f markdown -t rst - >| README.rst
