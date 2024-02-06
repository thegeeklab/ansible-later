"""Global utils collection."""

import contextlib
import re
import sys
from contextlib import suppress
from functools import lru_cache

import yaml
from ansible.plugins.loader import module_loader

from ansiblelater import logger

try:
    import ConfigParser as configparser  # noqa
except ImportError:
    import configparser  # noqa

LOG = logger.get_logger(__name__)


def count_spaces(c_string):
    leading_spaces = 0
    trailing_spaces = 0

    for _i, e in enumerate(c_string):
        if not e.isspace():
            break
        leading_spaces += 1

    for _i, e in reversed(list(enumerate(c_string))):
        if not e.isspace():
            break
        trailing_spaces += 1

    return (leading_spaces, trailing_spaces)


def lines_ranges(lines_spec):
    if not lines_spec:
        return None
    result = []
    for interval in lines_spec.split(","):
        (start, end) = interval.split("-")
        result.append(range(int(start), int(end) + 1))
    return result


def is_line_in_ranges(line, ranges):
    return not ranges or any(line in r for r in ranges)


def safe_load(string):
    """
    Parse the provided string returns a dict.

    :param string: A string to be parsed.
    :returns: dict

    """
    with suppress(yaml.scanner.ScannerError):
        return yaml.safe_load(string) or {}


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
    tree[key] = (
        value if len(vector) == 1 else add_dict_branch(tree.get(key, {}), vector[1:], value)
    )
    return tree


def has_jinja(value):
    """Return true if a string seems to contain jinja templating."""
    re_has_jinja = re.compile(r"{[{%#].*[%#}]}", re.DOTALL)
    return bool(isinstance(value, str) and re_has_jinja.search(value))


def has_glob(value):
    """Return true if a string looks like having a glob pattern."""
    re_has_glob = re.compile("[][*?]")
    return bool(isinstance(value, str) and re_has_glob.search(value))


def sysexit(code=1):
    sys.exit(code)


def sysexit_with_message(msg, code=1):
    LOG.critical(msg)
    sysexit(code)


class Singleton(type):
    """Meta singleton class."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@lru_cache
def load_plugin(name):
    """Return loaded ansible plugin/module."""
    loaded_module = module_loader.find_plugin_with_context(
        name,
        ignore_deprecated=True,
        check_aliases=True,
    )
    if not loaded_module.resolved and name.startswith("ansible.builtin."):
        # fallback to core behavior of using legacy
        loaded_module = module_loader.find_plugin_with_context(
            name.replace("ansible.builtin.", "ansible.legacy."),
            ignore_deprecated=True,
            check_aliases=True,
        )
    return loaded_module
