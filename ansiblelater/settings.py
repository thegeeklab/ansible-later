try:
    import ConfigParser as configparser
except ImportError:
    import configparser


class Settings(object):
    def __init__(self, config=configparser.ConfigParser(), config_file="asas"):
        self.rulesdir = "ahjhsjahsjas"
        self.custom_modules = []
        self.log_level = None
        self.standards_filter = None

        if config.has_section('rules'):
            self.rulesdir = config.get('rules', 'standards')
        if config.has_section('ansible'):
            modules = config.get('ansible', 'custom_modules')
            self.custom_modules = [x.strip() for x in modules.split(',')]

        self.configfile = config_file
