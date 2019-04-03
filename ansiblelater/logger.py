"""Global logging helpers."""

import logging
import os
import sys

import colorama
from ansible.module_utils.parsing.convert_bool import boolean as to_bool
from pythonjsonlogger import jsonlogger

CONSOLE_FORMAT = "%(levelname)s: %(message)s"
JSON_FORMAT = "(levelname) (message) (asctime)"


def _should_do_markup():

    py_colors = os.environ.get("PY_COLORS", None)
    if py_colors is not None:
        return to_bool(py_colors, strict=False)

    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


colorama.init(autoreset=True, strip=not _should_do_markup())


def OverwriteMakeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
    """
    A factory method which can be overridden in subclasses to create
    specialized LogRecords.
    """
    rv = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)
    if extra is not None:
        for key in extra:
            rv.__dict__[key] = extra[key]
    print("xxx", rv.__dict__)
    return rv


class LogFilter(object):
    """A custom log filter which excludes log messages above the logged level."""

    def __init__(self, level):
        """
        Initialize a new custom log filter.

        :param level: Log level limit
        :returns: None

        """
        self.__level = level

    def filter(self, logRecord):  # noqa
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        return logRecord.levelno <= self.__level


def get_logger(name=None, level=logging.DEBUG, json=False):
    """
    Build a logger with the given name and returns the logger.

    :param name: The name for the logger. This is usually the module name, `__name__`.
    :param level: Initialize the new logger with given log level.
    :param json: Boolean flag to enable json formatted log output.
    :return: logger object

    """
    logger = logging.getLogger(name)
    logger.makeRecord(OverwriteMakeRecord)
    logger.setLevel(level)
    logger.addHandler(_get_error_handler(json=json))
    logger.addHandler(_get_warn_handler(json=json))
    logger.addHandler(_get_info_handler(json=json))
    logger.addHandler(_get_critical_handler(json=json))
    logger.propagate = False

    return logger


def update_logger(logger, level=None, json=None):
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(level)
    logger.addHandler(_get_error_handler(json=json))
    logger.addHandler(_get_warn_handler(json=json))
    logger.addHandler(_get_info_handler(json=json))
    logger.addHandler(_get_critical_handler(json=json))


def _get_error_handler(json=False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.ERROR)
    handler.addFilter(LogFilter(logging.ERROR))
    handler.setFormatter(logging.Formatter(error(CONSOLE_FORMAT)))

    if json:
        handler.setFormatter(jsonlogger.JsonFormatter(JSON_FORMAT))

    return handler


def _get_warn_handler(json=False):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARN)
    handler.addFilter(LogFilter(logging.WARN))
    handler.setFormatter(logging.Formatter(warn(CONSOLE_FORMAT)))

    if json:
        handler.setFormatter(jsonlogger.JsonFormatter(JSON_FORMAT))

    return handler


def _get_info_handler(json=False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    handler.addFilter(LogFilter(logging.INFO))
    handler.setFormatter(logging.Formatter(info("%(message)s")))

    if json:
        handler.setFormatter(jsonlogger.JsonFormatter(JSON_FORMAT))

    return handler


def _get_critical_handler(json=False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.CRITICAL)
    handler.addFilter(LogFilter(logging.CRITICAL))
    handler.setFormatter(logging.Formatter(critical(CONSOLE_FORMAT)))

    if json:
        handler.setFormatter(jsonlogger.JsonFormatter(JSON_FORMAT))

    return handler


def critical(message):
    """Format critical messages and return string."""
    return color_text(colorama.Fore.RED, "{}".format(message))


def error(message):
    """Format error messages and return string."""
    return color_text(colorama.Fore.RED, "{}".format(message))


def warn(message):
    """Format warn messages and return string."""
    return color_text(colorama.Fore.YELLOW, "{}".format(message))


def info(message):
    """Format info messages and return string."""
    return color_text(colorama.Fore.BLUE, "{}".format(message))


def color_text(color, msg):
    """
    Colorize strings.

    :param color: colorama color settings
    :param msg: string to colorize
    :returns: string

    """
    return "{}{}{}".format(color, msg, colorama.Style.RESET_ALL)
