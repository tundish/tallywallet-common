#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # Includes bzr revsion number
    from tallywallet.common.about import version
except ImportError:
    try:
        # For setup.py install
        from tallywallet.common import __version__ as version
    except ImportError:
        # For pip installations
        version = str(ast.literal_eval(
                    open(os.path.join(os.path.dirname(__file__),
                    "tallywallet", "common", "__init__.py"),
                    'r').read().split("=")[-1].strip()))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.txt"),
               'r').read()

setup(
    name="tallywallet-common",
    version=version,
    description="A currency trading ledger in Python",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://www.assembla.com/spaces/tallywallet/messages",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        " or later (AGPLv3+)"
    ],
    namespace_packages=["tallywallet"],
    packages=[
        "tallywallet.common",
        "tallywallet.common.test",
    ],
    package_data={"tallywallet.common": [
                    "doc/*.rst",
                    "doc/_templates/*.css",
                    "doc/html/*.html",
                    "doc/html/*.js",
                    "doc/html/_sources/*",
                    "doc/html/_static/css/*",
                    "doc/html/_static/font/*",
                    "doc/html/_static/js/*",
                    "doc/html/_static/*.css",
                    "doc/html/_static/*.gif",
                    "doc/html/_static/*.js",
                    "doc/html/_static/*.png",
                    ]},
    install_requires=[],
    tests_require=["rson>=0.9"],
    entry_points={
        "console_scripts": [
        ],
    },
    zip_safe=False
)
