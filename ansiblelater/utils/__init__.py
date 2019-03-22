from __future__ import print_function

import importlib
import logging
import os
import sys
import re
import colorama

from distutils.version import LooseVersion
from ansible.module_utils.parsing.convert_bool import boolean as to_bool

try:
    import ConfigParser as configparser
except ImportError:
    import configparser


def should_do_markup():
    py_colors = os.environ.get('PY_COLORS', None)
    if py_colors is not None:
        return to_bool(py_colors, strict=False)

    return sys.stdout.isatty() and os.environ.get('TERM') != 'dumb'


colorama.init(autoreset=True, strip=not should_do_markup())


def abort(message, file=sys.stderr):
    return color_text(colorama.Fore.RED, "FATAL: {}".format(message))
    sys.exit(1)


def error(message, file=sys.stderr):
    return color_text(colorama.Fore.RED, "ERROR: {}".format(message))


def warn(message, settings, file=sys.stdout):
    if settings.log_level <= logging.WARNING:
        return color_text(colorama.Fore.YELLOW, "WARN: {}".format(message))


def info(message, settings, file=sys.stdout):
    if settings.log_level <= logging.INFO:
        return color_text(colorama.Fore.BLUE, "INFO: {}".format(message))


def color_text(color, msg):
    print('{}{}{}'.format(color, msg, colorama.Style.RESET_ALL))


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
        open(os.path.join(parentdir, '__init__.py')).read())
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


def read_standards(settings):
    if not settings.rulesdir:
        abort("Standards directory is not set on command line or in configuration file - aborting")
    sys.path.append(os.path.abspath(os.path.expanduser(settings.rulesdir)))
    try:
        standards = importlib.import_module('standards')
    except ImportError as e:
        abort("Could not import standards from directory %s: %s" % (settings.rulesdir, str(e)))
    return standards


def read_config(config_file):
    config = configparser.RawConfigParser({'standards': None})
    config.read(config_file)

    return Settings(config, config_file)


class Settings(object):
    def __init__(self, config, config_file):
        self.rulesdir = None
        self.custom_modules = []
        self.log_level = None
        self.standards_filter = None

        if config.has_section('rules'):
            self.rulesdir = config.get('rules', 'standards')
        if config.has_section('ansible'):
            modules = config.get('ansible', 'custom_modules')
            self.custom_modules = [x.strip() for x in modules.split(',')]

        self.configfile = config_file
