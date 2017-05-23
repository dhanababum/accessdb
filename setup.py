from __future__ import absolute_import
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as fp:
    readme = fp.read()

setup(
    name='accessdb',
    packages=['accessdb'],
    version='0.1',
    description='Fast way to create Access Database',
    long_description=readme,
    author='Dhana Babu',
    author_email='dhana36.m@gmail.com',
    url='https://github.com/dhanababum/accessdb',
    download_url='https://github.com/dhanababum/accessdb/archive/0.1.tar.gz',
    keywords=['python', 'accessdb', 'text'],
    classifiers=[],
)
