"""Global settings object definition."""

import os

import anyconfig
import pathspec
from appdirs import AppDirs
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
        self.schema = None
        self.args_files = False
        self.args = self._set_args(args)
        self.config = self._get_config()
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
        log_level = levels.index(defaults["logging"]["level"])
        if tmp_dict.get("logging"):
            for adjustment in tmp_dict["logging"]["level"]:
                log_level = min(len(levels) - 1, max(log_level + adjustment, 0))
            tmp_dict["logging"]["level"] = levels[log_level]

        if len(tmp_dict["rules"]["files"]) == 0:
            tmp_dict["rules"]["files"] = ["*"]
        else:
            tmp_dict["rules"]["files"] = tmp_dict["rules"]["files"]
            self.args_files = True

        return tmp_dict

    def _get_config(self):
        defaults = self._get_defaults()
        source_files = []
        source_files.append(self.config_file)
        source_files.append(os.path.relpath(
            os.path.normpath(os.path.join(os.getcwd(), ".later.yml"))))
        cli_options = self.args

        for config in source_files:
            if config and os.path.exists(config):
                with utils.open_file(config) as stream:
                    s = stream.read()
                    sdict = utils.safe_load(s)
                    if self._validate(sdict):
                        anyconfig.merge(defaults, sdict, ac_merge=anyconfig.MS_DICTS)
                        defaults["logging"]["level"] = defaults["logging"]["level"].upper()

        if cli_options and self._validate(cli_options):
            anyconfig.merge(defaults, cli_options, ac_merge=anyconfig.MS_DICTS)

        return defaults

    def _get_defaults(self):
        rules_dir = os.path.join(resource_filename("ansiblelater", "data"))
        defaults = {
            "rules": {
                "standards": rules_dir,
                "filter": [],
                "exclude_filter": [],
                "ignore_dotfiles": True,
                "exclude_files": []
            },
            "logging": {
                "level": "WARNING",
                "json": False
            },
            "ansible": {
                "custom_modules": [],
                "double-braces": {
                    "min-spaces-inside": 1,
                    "max-spaces-inside": 1,
                },
            },
            "yamllint": {
                "empty-lines": {
                    "max": 1,
                    "max-start": 0,
                    "max-end": 1,
                },
                "indentation": {
                    "spaces": 2,
                    "check-multi-line-strings": False,
                    "indent-sequences": True,
                },
                "hyphens": {
                    "max-spaces-after": 1
                },
                "document-start": {
                    "present": True
                },
                "colons": {
                    "max-spaces-before": 0,
                    "max-spaces-after": 1
                },
            },
        }

        self.schema = anyconfig.gen_schema(defaults)

        return defaults

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
        includes = self.config["rules"]["files"]
        excludes = self.config["rules"]["exclude_files"]
        ignore_dotfiles = self.config["rules"]["ignore_dotfiles"]

        if ignore_dotfiles and not self.args_files:
            excludes.append(".*")
        else:
            del excludes[:]

        filelist = []
        for root, dirs, files in os.walk("."):
            for filename in files:
                filelist.append(
                    os.path.relpath(os.path.normpath(os.path.join(root, filename))))

        valid = []
        includespec = pathspec.PathSpec.from_lines("gitwildmatch", includes)
        excludespec = pathspec.PathSpec.from_lines("gitwildmatch", excludes)
        for item in filelist:
            if includespec.match_file(item) and not excludespec.match_file(item):
                valid.append(item)

        self.config["rules"]["files"] = valid
