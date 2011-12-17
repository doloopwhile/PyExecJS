#python3
#encoding: shift-jis
from distutils.core import setup
import sys
import io
import execjs

with io.open('README.md', encoding='ascii') as fp:
    long_description = fp.read()

setup(
    packages=['execjs'],
    package_dir={'execjs': 'execjs'},
    package_data={
        'execjs': ['support/*.*'],
    },
    data_files = [
        ('', 'README.md LICENSE'.split()),
    ],
    
    name='PyExecJS',
    version=execjs.__version__,
    description='Run JavaScript code from Python ',
    long_description=long_description,
    author='Omoto Kenji',
    author_email='doloopwhile@gmail.com',
    url='https://github.com/doloopwhile/PyExecJS',
    
    license=execjs.__license__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.2',
        'Programming Language :: JavaScript',
    ],
)
