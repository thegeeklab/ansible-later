"""Global settings object definition."""

import copy
import logging
import os

import anyconfig
from appdirs import AppDirs
from globmatch import glob_match
from jsonschema._utils import format_as_index
from pkg_resources import resource_filename

from ansiblelater import utils

config_dir = AppDirs("ansible-later").user_config_dir
default_config_file = os.path.join(config_dir, "config.yml")


class Settings(object):
    """
    Create an object with all necessary settings.

    Settings are loade from multiple locations in defined order (last wins):
    - default settings defined by `self._get_defaults()`
    - yaml config file, defaults to OS specific user config dir (https://pypi.org/project/appdirs/)
    - provides cli parameters
    """

    def __init__(self, args={}, config_file=default_config_file):
        """
        Initialize a new settings class.

        :param args: An optional dict of options, arguments and commands from the CLI.
        :param config_file: An optional path to a yaml config file.
        :returns: None

        """
        self.config_file = config_file
        self.args = self._set_args(args)
        self.config = self._get_config()
        self.schema = None
        self._update_filelist()

    def _set_args(self, args):
        defaults = self._get_defaults()
        self.config_file = args.get("config_file") or default_config_file

        args.pop("config_file", None)
        tmp_args = dict(filter(lambda item: item[1] is not None, args.items()))

        tmp_dict = {}
        for key, value in tmp_args.items():
            tmp_dict = utils.add_dict_branch(tmp_dict, key.split("."), value)

        # Override correct log level from argparse
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        log_level = levels.index(logging.getLevelName(defaults["logging"]["level"]))
        if tmp_dict.get("logging"):
            for adjustment in tmp_dict["logging"]["level"]:
                log_level = min(len(levels) - 1, max(log_level + adjustment, 0))
            tmp_dict["logging"]["level"] = logging.getLevelName(levels[log_level])

        tmp_dict["rules"]["files"] = self._get_files(tmp_dict)

        return tmp_dict

    def _get_config(self):
        defaults = self._get_defaults()
        config_file = self.config_file
        cli_options = self.args

        if config_file and os.path.exists(config_file):
            with utils.open_file(config_file) as stream:
                s = stream.read()
                if self._validate(utils.safe_load(s)):
                    anyconfig.merge(defaults, utils.safe_load(s), ac_merge=anyconfig.MS_DICTS)

        if cli_options and self._validate(cli_options):
            anyconfig.merge(defaults, cli_options, ac_merge=anyconfig.MS_DICTS)

        return defaults

    def _get_defaults(self):
        rules_dir = os.path.join(resource_filename("ansiblelater", "data"))
        defaults = {
            "rules": {
                "standards": rules_dir,
                "filter": [],
                "ignore_dotfiles": True,
                "exclude_files": []
            },
            "logging": {
                "level": logging.getLevelName("WARNING"),
                "json": False
            },
            "ansible": {
                "custom_modules": [],
            }
        }
        self.schema = anyconfig.gen_schema(defaults)

        return defaults

    def _get_files(self, args):
        if len(args["rules"]["files"]) == 0:
            filelist = []
            for root, dirs, files in os.walk("."):
                for filename in files:
                    filelist.append(os.path.relpath(os.path.normpath(os.path.join(root, filename))))
        else:
            filelist = args["rules"]["files"]

        return filelist

    def _validate(self, config):
        try:
            anyconfig.validate(config, self.schema, ac_schema_safe=False)
            return True
        except Exception as e:
            schema_error = "Failed validating '{validator}' in schema{schema}".format(
                validator=e.validator,
                schema=format_as_index(list(e.relative_schema_path)[:-1])
            )
            utils.sysexit_with_message("{schema}: {msg}".format(schema=schema_error, msg=e.message))

    def _update_filelist(self):
        files = self.config["rules"]["files"]
        excludes = self.config["rules"]["exclude_files"]
        ignore_dotfiles = self.config["rules"]["ignore_dotfiles"]

        if ignore_dotfiles:
            excludes.append(".")

        valid = copy.copy(files)
        for item in valid:
            if glob_match(item, excludes):
                files.remove(item)
