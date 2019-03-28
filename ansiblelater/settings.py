import json
import logging
import os

import anyconfig
from pkg_resources import resource_filename

from ansiblelater import utils

try:
    import ConfigParser as configparser
except ImportError:
    import configparser


class Settings(object):
    def __init__(self, args={}):
        self.args = self._get_args(args)
        self.config = self._get_config()

    def _get_args(self, args):
        # Override correct log level from argparse
        levels = [logging.WARNING, logging.INFO, logging.DEBUG]
        if args.log_level:
            args.log_level = levels[min(len(levels) - 1, args.log_level - 1)]

        args_dict = dict(filter(lambda item: item[1] is not None, args.__dict__.items()))
        return args_dict

    def _get_config(self):
        defaults = self._get_defaults()
        config_file = self.args.get('config_file')

        if config_file and os.path.exists(config_file):
            with utils.open_file(config_file) as stream:
                s = stream.read()
                anyconfig.merge(defaults, utils.safe_load(s), ac_merge=anyconfig.MS_DICTS)

        print(json.dumps(defaults, indent=4, sort_keys=True))
        return defaults

    def _get_defaults(self):
        rules_dir = os.path.join(resource_filename('ansiblelater', 'examples'))

        return {
            'rules': {
                'standards': self.args.get('rules_dir', rules_dir),
                'standards_filter': [],
            },
            'logging': {
                'level': self.args.get('log_level', logging.WARN),
            },
            'ansible': {
                'custom_modules': [],
            }
        }
