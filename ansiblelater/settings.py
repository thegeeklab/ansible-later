import logging
import os
import six

import anyconfig
from appdirs import AppDirs
from pkg_resources import resource_filename

from ansiblelater import utils, logger

config_dir = AppDirs("ansible-later").user_config_dir
default_config_file = os.path.join(config_dir, "config.yml")

logger = logger.get_logger(__name__)


class NewInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.after_init()
        return obj


@six.add_metaclass(NewInitCaller)
class Settings(object):
    def __init__(self, args={}, config_file=default_config_file):
        self.args = args
        self.config_file = config_file
        self.config = self._get_config()

    def set_args(self, args={}):
        self.config_file = args.get("config_file") or default_config_file

        args.pop("config_file", None)
        args = dict(filter(lambda item: item[1] is not None, args.items()))

        args_dict = {}
        for key, value in args.items():
            args_dict = utils.add_dict_branch(args_dict, key.split("."), value)

        self.args = args_dict
        self.config = self._get_config()
        self._validate()

    def _get_config(self):
        defaults = self._get_defaults()
        config_file = self.config_file
        cli_options = self.args

        if config_file and os.path.exists(config_file):
            with utils.open_file(config_file) as stream:
                s = stream.read()
                anyconfig.merge(defaults, utils.safe_load(s), ac_merge=anyconfig.MS_DICTS)

        if cli_options:
            anyconfig.merge(defaults, cli_options, ac_merge=anyconfig.MS_DICTS)

        return defaults

    def _get_defaults(self):
        rules_dir = os.path.join(resource_filename('ansiblelater', 'examples'))

        return {
            'rules': {
                'standards': rules_dir,
                'filter': [],
            },
            'logging': {
                'level': logging.WARN,
            },
            'ansible': {
                'custom_modules': [],
            }
        }

    def after_init(self):
        self.config = self._get_config()
        self._validate()

    def _validate(self):
        logger.setLevel(self.config["logging"]["level"])

