"""Global utils collection."""

from __future__ import print_function

import contextlib
import os
import re
import sys
from distutils.version import LooseVersion

import yaml

from ansiblelater import logger

try:
    import ConfigParser as configparser # noqa
except ImportError:
    import configparser # noqa


LOG = logger.get_logger(__name__)


def count_spaces(c_string):
    leading_spaces = 0
    trailing_spaces = 0

    for i, e in enumerate(c_string):
        if not e.isspace():
            break
        leading_spaces += 1

    for i, e in reversed(list(enumerate(c_string))):
        if not e.isspace():
            break
        trailing_spaces += 1

    return((leading_spaces, trailing_spaces))


def get_property(prop):
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    result = re.search(
        r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
        open(os.path.join(parentdir, "__init__.py")).read())
    return result.group(1)


def standards_latest(standards):
    return max([standard.version for standard in standards if standard.version] or ["0.1"],
               key=LooseVersion)


def lines_ranges(lines_spec):
    if not lines_spec:
        return None
    result = []
    for interval in lines_spec.split(","):
        (start, end) = interval.split("-")
        result.append(range(int(start), int(end) + 1))
    return result


def is_line_in_ranges(line, ranges):
    return not ranges or any([line in r for r in ranges])


def safe_load(string):
    """
    Parse the provided string returns a dict.

    :param string: A string to be parsed.
    :returns: dict

    """
    try:
        return yaml.safe_load(string) or {}
    except yaml.scanner.ScannerError as e:
        print(str(e))


@contextlib.contextmanager
def open_file(filename, mode="r"):
    """
    Open the provide file safely and returns a file type.

    :param filename: A string containing an absolute path to the file to open.
    :param mode: A string describing the way in which the file will be used.
    :returns: file type

    """
    with open(filename, mode) as stream:
        yield stream


def add_dict_branch(tree, vector, value):
    key = vector[0]
    tree[key] = value \
        if len(vector) == 1 \
        else add_dict_branch(tree[key] if key in tree else {},
                             vector[1:],
                             value)
    return tree


def sysexit(code=1):
    sys.exit(code)


def sysexit_with_message(msg, code=1):
    LOG.critical(msg)
    sysexit(code)
