#!/usr/bin/env python
from setuptools import setup, find_packages

import re
import sys
import os

BASE_LOCATION = os.path.abspath(os.path.dirname(__file__))

VERSION_FILE = os.path.join(BASE_LOCATION, 'src', 'pyMediaSort', '__init__.py')
REQUIRES_FILE = 'requirements.txt'
DEPENDENCIES_FILE = None


def filter_comments(fd):
    no_comments = list(filter(lambda l: l.strip().startswith("#") is False, fd.readlines()))
    return list(filter(lambda l: l.strip().startswith("-") is False, no_comments))


def readfile(filename, func):
    try:
        with open(os.path.join(BASE_LOCATION, filename)) as f:
            data = func(f)
    except (IOError, IndexError):
        sys.stderr.write(u"""
Can't find '%s' file. This doesn't seem to be a valid release.
""" % filename)
        sys.exit(1)
    return data


def get_version():
    with open(VERSION_FILE, 'r') as f:
        data = f.read()
        m = re.search(r"__version__ ?= ?'[\d\.]+'", data)
    res = m.group(0)
    if res:
        ret = re.search(r"(?<=')[\d\.]+", res).group(0)
        if ret:
            return ret
    raise ValueError("No version for package found")


def get_requires():
    return readfile(REQUIRES_FILE, filter_comments)


def get_dependencies():
    return readfile(DEPENDENCIES_FILE, filter_comments)


setup(
    name="pyMediaSort",
    author="Christopher Wallis",
    author_email="christopher.wallis@gmail.com",
    description="Package for sorting media into Plex directory structure",
    keywords="sort media tv video plex",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=[],
    url="https://github.com/christopherwallis/pyMediaSort",
    version=get_version(),
    install_requires=[],
    python_requires='~=3.7',
    dependency_links=[],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only"
    ],
    entry_points={
        'console_scripts': [
            'sorttv=pyMediaSort.SortTV:main'
        ],
    }
)
