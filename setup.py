#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # Includes bzr revsion number
    from topicmob.web.about import version
except ImportError:
    try:
        # For setup.py install
        from topicmob.web import __version__ as version
    except ImportError:
        # For pip installations
        version = str(ast.literal_eval(
                    open(os.path.join(os.path.dirname(__file__),
                    "topicmob", "web", "__init__.py"),
                    'r').read().split("=")[-1].strip()))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.txt"),
               'r').read()

setup(
    name="topicmob-web",
    version=version,
    description="A TopicMob component, containing the web application",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="http://www.thuswise.co.uk",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        " or later (AGPLv3+)"
    ],
    namespace_packages=["topicmob"],
    packages=["topicmob.web"],
    package_data={"topicmob.web": [
                    "templates/*.pt",
                    "static/css/*.css",
                    "static/html/*.html",
                    "static/js/*.js",
                    "static/img/*.png",
                    ]},
    test_suite="topicmob.web.test_main",
    tests_require=[
        "WebTest>=2.0.0",
        ],
    install_requires=[
        "pyramid>=1.4.0",
        "pyramid-persona>=1.4",
        "waitress>=0.8.5",
        "topicmob-schema>=0.016",
        "topicmob-model>=0.015"],
    entry_points={
        "console_scripts": [
        "tm-web = topicmob.web.main:run"
        ],
    },
    zip_safe=False
)

