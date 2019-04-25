#!/usr/bin/env python
"""Setup script for the package."""

import io
import os
import re

from setuptools import find_packages, setup

PACKAGE_NAME = "ansiblelater"


def get_property(prop, project):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    result = re.search(
        r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
        open(os.path.join(current_dir, project, "__init__.py")).read())
    return result.group(1)


def get_readme(filename="README.md"):
    this = os.path.abspath(os.path.dirname(__file__))
    with io.open(os.path.join(this, filename), encoding="utf-8") as f:
        long_description = f.read()
    return long_description


setup(
    name=get_property("__project__", PACKAGE_NAME),
    version=get_property("__version__", PACKAGE_NAME),
    description=("Reviews ansible playbooks, roles and inventories and suggests improvements."),
    keywords="ansible code review",
    author=get_property("__author__", PACKAGE_NAME),
    author_email=get_property("__email__", PACKAGE_NAME),
    url="https://github.com/xoxys/ansible-later",
    license=get_property("__license__", PACKAGE_NAME),
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*.tests", "tests", "tests.*"]),
    package_data={"ansiblelater": ["data/*"]},
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,,!=3.4.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "ansible",
        "six",
        "pyyaml",
        "appdirs",
        "unidiff",
        "flake8",
        "yamllint",
        "nested-lookup",
        "colorama",
        "anyconfig",
        "python-json-logger",
        "jsonschema",
        "pathspec",
        "toolz"
    ],
    entry_points={
        "console_scripts": [
            "ansible-later = ansiblelater.__main__:main"
        ]
    },
    test_suite="tests"
)
