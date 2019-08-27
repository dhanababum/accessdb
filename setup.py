from __future__ import absolute_import
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(PACKAGE_PATH, 'README.md'), encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name='accessdb',
    packages=['accessdb'],
    version='0.0.1',
    description='Fast way to create Access Database',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Dhana Babu',
    author_email='dhana36.m@gmail.com',
    url='https://github.com/dhanababum/accessdb',
    download_url='https://github.com/dhanababum/accessdb/archive/0.1.tar.gz',
    keywords=['python', 'accessdb', 'text'],
    classifiers=[],
)
