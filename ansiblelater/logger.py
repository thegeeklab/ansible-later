import logging
import os
import sys

import colorama
from pythonjsonlogger import jsonlogger
from ansible.module_utils.parsing.convert_bool import boolean as to_bool


def should_do_markup():
    py_colors = os.environ.get('PY_COLORS', None)
    if py_colors is not None:
        return to_bool(py_colors, strict=False)

    return sys.stdout.isatty() and os.environ.get('TERM') != 'dumb'


colorama.init(autoreset=True, strip=not should_do_markup())


class LogFilter(object):
    """
    A custom log filter which excludes log messages above the logged
    level.
    """

    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):  # pragma: no cover
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        return logRecord.levelno <= self.__level


def get_logger(name=None, level=logging.DEBUG, json=False):
    """
    Build a logger with the given name and returns the logger.
    :param name: The name for the logger. This is usually the module
                 name, ``__name__``.
    :return: logger object
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    #handler = logging.StreamHandler()
    #formatter = jsonlogger.JsonFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #handler.setFormatter(formatter)
    logger.addHandler(_get_error_handler(json=json))
    logger.addHandler(_get_warn_handler(json=json))
    logger.addHandler(_get_info_handler(json=json))
    logger.propagate = False

    return logger


def _get_error_handler(json=False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.ERROR)
    handler.addFilter(LogFilter(logging.ERROR))
    handler.setFormatter(logging.Formatter(error('%(message)s')))

    if json:
        handler.setFormatter(jsonlogger.JsonFormatter('%(message)s'))

    return handler


def _get_warn_handler(json=False):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARN)
    handler.addFilter(LogFilter(logging.WARN))
    handler.setFormatter(logging.Formatter(warn('%(message)s')))

    if json:
        handler.setFormatter(jsonlogger.JsonFormatter('%(message)s'))

    return handler


def _get_info_handler(json=False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    handler.addFilter(LogFilter(logging.INFO))
    handler.setFormatter(logging.Formatter(info('%(message)s')))

    if json:
        handler.setFormatter(jsonlogger.JsonFormatter('%(message)s'))

    return handler


def abort(message, file=sys.stderr):
    return color_text(colorama.Fore.RED, "FATAL: {}".format(message))
    sys.exit(1)


def error(message):
    return color_text(colorama.Fore.RED, "ERROR: {}".format(message))


def warn(message):
    return color_text(colorama.Fore.YELLOW, "WARN: {}".format(message))


def info(message):
    return color_text(colorama.Fore.BLUE, "INFO: {}".format(message))


def color_text(color, msg):
    return '{}{}{}'.format(color, msg, colorama.Style.RESET_ALL)
