#!/bin/bash
python -c "import sys; sys.version_info >= (2, 7) or sys.exit(1)"
if [ $? -ne 0 ]; then
  pip install unittest2
fi
pip install six
