"""Base methods."""

import importlib
import os
import sys
from distutils.version import LooseVersion

import ansible

from ansiblelater import settings, utils


def get_settings(args):
    """
    Get new settings object.

    :param args: cli args from argparse
    :returns: Settings object

    """
    config = settings.Settings(
        args=args,
    )

    return config


def get_standards(filepath):
        sys.path.append(os.path.abspath(os.path.expanduser(filepath)))
        try:
            standards = importlib.import_module("standards")
        except ImportError as e:
            utils.sysexit_with_message(
                "Could not import standards from directory %s: %s" % (filepath, str(e)))

        if getattr(standards, "ansible_min_version", None) and \
                LooseVersion(standards.ansible_min_version) > LooseVersion(ansible.__version__):
            utils.sysexit_with_message("Standards require ansible version %s (current version %s). "
                                       "Please upgrade ansible." %
                                       (standards.ansible_min_version, ansible.__version__))

        if getattr(standards, "ansible_review_min_version", None) and \
                LooseVersion(standards.ansible_review_min_version) > LooseVersion(
                    utils.get_property("__version__")):
            utils.sysexit_with_message(
                "Standards require ansible-later version %s (current version %s). "
                "Please upgrade ansible-later." %
                (standards.ansible_review_min_version, utils.get_property("__version__")))

        return standards.standards
