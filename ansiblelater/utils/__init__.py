from __future__ import print_function

import importlib
import logging
import os
import subprocess
import sys
import re

from distutils.version import LooseVersion

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

try:
    from ansible.utils.color import stringc
except ImportError:
    from ansible.color import stringc

# from yamlhelper import *


def abort(message, file=sys.stderr):
    print(stringc("FATAL: %s" % message, 'red'), file=file)
    sys.exit(1)


def error(message, file=sys.stderr):
    print(stringc("ERROR: %s" % message, 'red'), file=file)


def warn(message, settings, file=sys.stdout):
    if settings.log_level <= logging.WARNING:
        print(stringc("WARN: %s" % message, 'yellow'), file=file)


def info(message, settings, file=sys.stdout):
    if settings.log_level <= logging.INFO:
        print(stringc("INFO: %s" % message, 'green'), file=file)


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


def execute(cmd):
    result = ExecuteResult()
    encoding = 'UTF-8'
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = encoding
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env=env)
    result.output = proc.communicate()[0].decode(encoding)
    result.rc = proc.returncode
    return result


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


class ExecuteResult(object):
    pass
