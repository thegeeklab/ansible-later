"""Global settings object definition."""

import importlib.resources
import os

import anyconfig
import jsonschema.exceptions
import pathspec
from appdirs import AppDirs
from jsonschema._utils import format_as_index

from ansiblelater import utils

config_dir = AppDirs("ansible-later").user_config_dir
default_config_file = os.path.join(config_dir, "config.yml")


class Settings:
    """
    Create an object with all necessary settings.

    Settings are loade from multiple locations in defined order (last wins):
    - default settings defined by `self._get_defaults()`
    - yaml config file, defaults to OS specific user config dir (https://pypi.org/project/appdirs/)
    - provides cli parameters
    """

    def __init__(self, args, config_file=default_config_file):
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
        if args is None:
            args = {}

        defaults = self._get_defaults()
        self.config_file = args.get("config_file") or default_config_file

        tmp_args = dict(filter(lambda item: item[1] is not None, args.items()))
        tmp_args.pop("config_file", None)

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
        source_files.append(os.path.join(os.getcwd(), ".later"))
        source_files.append(os.path.join(os.getcwd(), ".later.yml"))
        source_files.append(os.path.join(os.getcwd(), ".later.yaml"))
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

        library = os.path.relpath(os.path.normpath(os.path.join(os.getcwd(), "library")))
        autodetect = []
        if os.path.exists(library):
            autodetect = [
                os.path.splitext(f)[0]
                for f in os.listdir(library)
                if os.path.isfile(os.path.join(library, f)) and not f.startswith(".")
            ]

        for f in autodetect:
            if f not in defaults["ansible"]["custom_modules"]:
                defaults["ansible"]["custom_modules"].append(f)

        if defaults["rules"]["builtin"]:
            ref = importlib.resources.files("ansiblelater") / "rules"
            with importlib.resources.as_file(ref) as path:
                defaults["rules"]["dir"].append(path)

        defaults["rules"]["dir"] = [
            os.path.relpath(os.path.normpath(p)) for p in defaults["rules"]["dir"]
        ]

        return defaults

    def _get_defaults(self):
        defaults = {
            "rules": {
                "builtin": True,
                "dir": [],
                "include_filter": [],
                "exclude_filter": [],
                "warning_filter": [
                    "ANS128",
                    "ANS999",
                ],
                "ignore_dotfiles": True,
                "exclude_files": [],
            },
            "logging": {
                "level": "WARNING",
                "json": False,
            },
            "ansible": {
                "custom_modules": [],
                "double-braces": {
                    "min-spaces-inside": 1,
                    "max-spaces-inside": 1,
                },
                "literal-bools": ["True", "False", "yes", "no"],
                "named-task": {
                    "exclude": [
                        "meta",
                        "debug",
                        "block/always/rescue",
                        "include_role",
                        "import_role",
                        "include_tasks",
                        "import_tasks",
                        "include_vars",
                    ],
                },
                "native-yaml": {
                    "exclude": [],
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
                    "max-spaces-after": 1,
                },
                "document-start": {
                    "present": True,
                },
                "document-end": {
                    "present": False,
                },
                "colons": {
                    "max-spaces-before": 0,
                    "max-spaces-after": 1,
                },
                "octal-values": {
                    "forbid-implicit-octal": True,
                    "forbid-explicit-octal": True,
                },
            },
        }

        self.schema = anyconfig.gen_schema(defaults)

        return defaults

    def _validate(self, config):
        try:
            anyconfig.validate(config, self.schema, ac_schema_safe=False)
            return True
        except jsonschema.exceptions.ValidationError as e:
            validator = e.validator
            path = format_as_index(
                next(iter(e.absolute_path)),
                list(e.absolute_path)[1:],
            )
            msg = e.message

            utils.sysexit_with_message(
                "Error while loading configuration:\n"
                f"Failed validating '{validator}' at {path}: {msg}"
            )

    def _update_filelist(self):
        includes = self.config["rules"]["files"]
        excludes = self.config["rules"]["exclude_files"]
        ignore_dotfiles = self.config["rules"]["ignore_dotfiles"]

        if ignore_dotfiles:
            excludes.append(".*")

        if self.args_files:
            del excludes[:]

        filelist = []
        for root, _dirs, files in os.walk("."):
            for filename in files:
                filelist.append(os.path.relpath(os.path.normpath(os.path.join(root, filename))))

        valid = []
        includespec = pathspec.PathSpec.from_lines("gitwildmatch", includes)
        excludespec = pathspec.PathSpec.from_lines("gitwildmatch", excludes)
        for item in filelist:
            if includespec.match_file(item) and not excludespec.match_file(item):
                valid.append(item)

        self.config["rules"]["files"] = valid
