#!/usr/bin/env python

import logging
import optparse
import os
import sys
from appdirs import AppDirs
from pkg_resources import resource_filename
from ansiblelater import classify
from ansiblelater.utils import info, warn, read_config, get_property


def main():
    config_dir = AppDirs("ansible-later").user_config_dir
    default_config_file = os.path.join(config_dir, "config.ini")

    parser = optparse.OptionParser("%prog playbook_file|role_file|inventory_file",
                                   version="%prog " + get_property("__version__"))
    parser.add_option('-c', dest='configfile', default=default_config_file,
                      help="Location of configuration file: [%s]" % default_config_file)
    parser.add_option('-d', dest='rulesdir',
                      help="Location of standards rules")
    parser.add_option('-q', dest='log_level', action="store_const", default=logging.WARN,
                      const=logging.ERROR, help="Only output errors")
    parser.add_option('-s', dest='standards_filter', action='append',
                      help="limit standards to specific names")
    parser.add_option('-v', dest='log_level', action="store_const", default=logging.WARN,
                      const=logging.INFO, help="Show more verbose output")

    options, args = parser.parse_args(sys.argv[1:])
    settings = read_config(options.configfile)

    # Merge CLI options with config options. CLI options override config options.
    for key, value in options.__dict__.items():
        if value:
            setattr(settings, key, value)

    if os.path.exists(settings.configfile):
        info("Using configuration file: %s" % settings.configfile, settings)
    else:
        warn("No configuration file found at %s" % settings.configfile, settings, file=sys.stderr)
        if not settings.rulesdir:
            rules_dir = os.path.join(resource_filename('ansiblelater', 'examples'))
            warn("Using example standards found at %s" % rules_dir, settings, file=sys.stderr)
            settings.rulesdir = rules_dir

    if len(args) == 0:
        candidates = []
        for root, dirs, files in os.walk("."):
            for filename in files:
                candidates.append(os.path.join(root, filename))
    else:
        candidates = args

    errors = 0
    for filename in candidates:
        if ':' in filename:
            (filename, lines) = filename.split(":")
        else:
            lines = None
        candidate = classify(filename)
        if candidate:
            if candidate.binary:
                info("Not reviewing binary file %s" % filename, settings)
                continue
            if candidate.vault:
                info("Not reviewing vault file %s" % filename, settings)
                continue
            if lines:
                info("Reviewing %s lines %s" % (candidate, lines), settings)
            else:
                info("Reviewing all of %s" % candidate, settings)
            errors = errors + candidate.review(settings, lines)
        else:
            info("Couldn't classify file %s" % filename, settings)
    return errors


if __name__ == "__main__":
    main()
