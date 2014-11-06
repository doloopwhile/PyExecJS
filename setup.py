#!python3
#encoding:ascii
from __future__ import division, with_statement
version = '1.0.5'
author = "Omoto Kenji"
license = "MIT License"
author_email = 'doloopwhile@gmail.com'

from setuptools import setup, find_packages
import sys
import io

with io.open('README.rst', encoding='ascii') as fp:
    long_description = fp.read()

if sys.version_info < (2, 7):
    install_requires = "argparse ordereddict".split()
else:
    install_requires = []

setup(
    packages=find_packages(),
    include_package_data=True,
    name='PyExecJS',
    version=version,
    description='Run JavaScript code from Python',
    long_description=long_description,
    author=author,
    author_email=author_email,
    url='https://github.com/doloopwhile/PyExecJS',
    license=license,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: JavaScript',
    ],
    install_requires=install_requires,
    test_suite="test_execjs",
)
