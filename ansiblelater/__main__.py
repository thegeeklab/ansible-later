#!/usr/bin/env python

import argparse
import json
import logging
import os

from ansiblelater import __version__
from ansiblelater.command import base


def main():
    parser = argparse.ArgumentParser(
        description="Validate ansible files against best pratice guideline")
    parser.add_argument("-c", dest="config_file",
                        help="Location of configuration file")
    parser.add_argument("-d", dest="rules.standards",
                        help="Location of standards rules")
    parser.add_argument("-q", dest="logging.level", action="store_const",
                        const=logging.ERROR, help="Only output errors")
    parser.add_argument("-s", dest="rules.filter", action="append",
                        help="limit standards to specific names")
    parser.add_argument("-v", "--verbose", dest="logging.level", action="count",
                        help="Show more verbose output")
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(__version__))

    args = parser.parse_args().__dict__

    settings = base.get_settings(args)
    print(json.dumps(settings.config, indent=4, sort_keys=True))

    # if len(args) == 0:
    #     candidates = []
    #     for root, dirs, files in os.walk("."):
    #         for filename in files:
    #             candidates.append(os.path.join(root, filename))
    # else:
    #     candidates = args

    # errors = 0
    # for filename in candidates:
    #     if ":" in filename:
    #         (filename, lines) = filename.split(":")
    #     else:
    #         lines = None
    #     candidate = classify(filename)
    #     if candidate:
    #         if candidate.binary:
    #             info("Not reviewing binary file %s" % filename, settings)
    #             continue
    #         if candidate.vault:
    #             info("Not reviewing vault file %s" % filename, settings)
    #             continue
    #         if lines:
    #             info("Reviewing %s lines %s" % (candidate, lines), settings)
    #         else:
    #             info("Reviewing all of %s" % candidate, settings)
    #         errors = errors + candidate.review(settings, lines)
    #     else:
    #         info("Couldn't classify file %s" % filename, settings)
    # return errors


if __name__ == "__main__":
    main()
