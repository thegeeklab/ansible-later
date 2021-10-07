"""Global logging helpers."""

import logging
import os
import sys
from distutils.util import strtobool

import colorama
from pythonjsonlogger import jsonlogger

CONSOLE_FORMAT = "{}%(levelname)s:{} %(message)s"
JSON_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def to_bool(string):
    return bool(strtobool(str(string)))


def _should_do_markup():

    py_colors = os.environ.get("PY_COLORS", None)
    if py_colors is not None:
        return to_bool(py_colors)

    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


colorama.init(autoreset=True, strip=(not _should_do_markup()))


def flag_extra(extra):
    """Ensure extra args are prefixed."""
    flagged = dict()

    if isinstance(extra, dict):
        for key, value in extra.items():
            flagged["later_" + key] = value

    return flagged


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


class MultilineFormatter(logging.Formatter):
    """Logging Formatter to reset color after newline characters."""

    def format(self, record):  # noqa
        record.msg = record.msg.replace("\n", "\n{}... ".format(colorama.Style.RESET_ALL))
        record.msg = record.msg + "\n"
        return logging.Formatter.format(self, record)


class MultilineJsonFormatter(jsonlogger.JsonFormatter):
    """Logging Formatter to remove newline characters."""

    def format(self, record):  # noqa
        record.msg = record.msg.replace("\n", " ")
        return jsonlogger.JsonFormatter.format(self, record)


def get_logger(name=None, level=logging.DEBUG, json=False):
    """
    Build a logger with the given name and returns the logger.

    :param name: The name for the logger. This is usually the module name, `__name__`.
    :param level: Initialize the new logger with given log level.
    :param json: Boolean flag to enable json formatted log output.
    :return: logger object

    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(_get_error_handler(json=json))
    logger.addHandler(_get_warn_handler(json=json))
    logger.addHandler(_get_info_handler(json=json))
    logger.addHandler(_get_critical_handler(json=json))
    logger.propagate = False

    return logger


def update_logger(logger, level=None, json=None):
    """Update logger configuration to change logging settings."""
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
    handler.setFormatter(MultilineFormatter(error(CONSOLE_FORMAT)))

    if json:
        handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))

    return handler


def _get_warn_handler(json=False):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARN)
    handler.addFilter(LogFilter(logging.WARN))
    handler.setFormatter(MultilineFormatter(warn(CONSOLE_FORMAT)))

    if json:
        handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))

    return handler


def _get_info_handler(json=False):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.addFilter(LogFilter(logging.INFO))
    handler.setFormatter(MultilineFormatter(info(CONSOLE_FORMAT)))

    if json:
        handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))

    return handler


def _get_critical_handler(json=False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.CRITICAL)
    handler.addFilter(LogFilter(logging.CRITICAL))
    handler.setFormatter(MultilineFormatter(critical(CONSOLE_FORMAT)))

    if json:
        handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))

    return handler


def critical(message):
    """Format critical messages and return string."""
    return color_text(colorama.Fore.RED, message)


def error(message):
    """Format error messages and return string."""
    return color_text(colorama.Fore.RED, message)


def warn(message):
    """Format warn messages and return string."""
    return color_text(colorama.Fore.YELLOW, message)


def info(message):
    """Format info messages and return string."""
    return color_text(colorama.Fore.BLUE, message)


def color_text(color, msg):
    """
    Colorize strings.

    :param color: colorama color settings
    :param msg: string to colorize
    :returns: string

    """
    msg = msg.format(colorama.Style.BRIGHT, colorama.Style.NORMAL)
    return "{}{}{}".format(color, msg, colorama.Style.RESET_ALL)
