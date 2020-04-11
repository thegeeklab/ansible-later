"""Base methods."""

import importlib
import os
import sys
from distutils.version import LooseVersion

import ansible
import toolz

from ansiblelater import settings
from ansiblelater import utils


def get_settings(args):
    """
    Get new settings object.

    :param args: cli args from argparse
    :returns: Settings object

    """
    config = settings.Settings(args=args)

    return config


def get_standards(filepath):
    sys.path.append(os.path.abspath(os.path.expanduser(filepath)))
    try:
        standards = importlib.import_module("standards")
    except ImportError as e:
        utils.sysexit_with_message(
            "Could not import standards from directory {path}: {msg}".format(
                path=filepath, msg=str(e)
            )
        )

    if getattr(standards, "ansible_min_version", None) and \
            LooseVersion(standards.ansible_min_version) > LooseVersion(ansible.__version__):
        utils.sysexit_with_message(
            "Standards require ansible version {min_version} (current version {version}). "
            "Please upgrade ansible.".format(
                min_version=standards.ansible_min_version, version=ansible.__version__
            )
        )

    if getattr(standards, "ansible_later_min_version", None) and \
            LooseVersion(standards.ansible_later_min_version) > LooseVersion(
                utils.get_property("__version__")):
        utils.sysexit_with_message(
            "Standards require ansible-later version {min_version} (current version {version}). "
            "Please upgrade ansible-later.".format(
                min_version=standards.ansible_later_min_version,
                version=utils.get_property("__version__")
            )
        )

    normalized_std = (list(toolz.remove(lambda x: x.id == "", standards.standards)))
    unique_std = len(list(toolz.unique(normalized_std, key=lambda x: x.id)))
    all_std = len(normalized_std)
    if not all_std == unique_std:
        utils.sysexit_with_message(
            "Detect duplicate ID's in standards definition. Please use unique ID's only."
        )

    return standards.standards
