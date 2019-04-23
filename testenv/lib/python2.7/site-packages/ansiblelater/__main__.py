#!/usr/bin/env python
"""Main program."""

import argparse
import multiprocessing
import sys

from ansiblelater import LOG
from ansiblelater import __version__
from ansiblelater import logger
from ansiblelater.command import base
from ansiblelater.command import candidates


def main():
    """Run main program."""
    parser = argparse.ArgumentParser(
        description="Validate ansible files against best pratice guideline")
    parser.add_argument("-c", "--config", dest="config_file",
                        help="location of configuration file")
    parser.add_argument("-r", "--rules", dest="rules.standards",
                        help="location of standards rules")
    parser.add_argument("-s", "--standards", dest="rules.filter", action="append",
                        help="limit standards to given ID's")
    parser.add_argument("-x", "--exclude-standards", dest="rules.exclude_filter", action="append",
                        help="exclude standards by given ID's")
    parser.add_argument("-v", dest="logging.level", action="append_const", const=-1,
                        help="increase log level")
    parser.add_argument("-q", dest="logging.level", action="append_const",
                        const=1, help="decrease log level")
    parser.add_argument("rules.files", nargs="*")
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(__version__))

    args = parser.parse_args().__dict__

    settings = base.get_settings(args)
    config = settings.config

    logger.update_logger(LOG, config["logging"]["level"], config["logging"]["json"])

    files = config["rules"]["files"]
    standards = base.get_standards(config["rules"]["standards"])

    workers = max(multiprocessing.cpu_count() - 2, 2)
    p = multiprocessing.Pool(workers)
    tasks = []
    for filename in files:
        lines = None
        candidate = candidates.classify(filename, settings, standards)
        if candidate:
            if candidate.binary:
                LOG.info("Not reviewing binary file %s" % filename)
                continue
            if candidate.vault:
                LOG.info("Not reviewing vault file %s" % filename)
                continue
            if lines:
                LOG.info("Reviewing %s lines %s" % (candidate, lines))
            else:
                LOG.info("Reviewing all of %s" % candidate)
                tasks.append((candidate, settings, lines))
        else:
            LOG.info("Couldn't classify file %s" % filename)

    errors = (sum(p.map(_review_wrapper, tasks)))
    p.close()
    p.join()

    if not errors == 0:
        return_code = 1
    else:
        return_code = 0

    sys.exit(return_code)


def _review_wrapper(args):
    (candidate, settings, lines) = args
    return candidate.review(settings, lines)


if __name__ == "__main__":
    main()
