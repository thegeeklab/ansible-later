#!/usr/bin/env python
"""Main program."""

import argparse
import json
import multiprocessing

from ansiblelater import LOG, __version__, logger
from ansiblelater.command import base, candidates


def main():
    """Run main program."""
    parser = argparse.ArgumentParser(
        description="Validate ansible files against best pratice guideline")
    parser.add_argument("-c", "--config", dest="config_file",
                        help="Location of configuration file")
    parser.add_argument("-r", "--rules", dest="rules.standards",
                        help="Location of standards rules")
    parser.add_argument("-q", "--quiet", dest="logging.level", action="append_const",
                        const=1, help="Only output errors")
    parser.add_argument("-s", "--standards", dest="rules.filter", action="append",
                        help="limit standards to specific names")
    parser.add_argument("-v", dest="logging.level", action="append_const", const=-1,
                        help="Show more verbose output")
    parser.add_argument("rules.files", nargs="*")
    parser.add_argument("--version", action="version", version="%(prog)s {}".format(__version__))

    args = parser.parse_args().__dict__

    settings = base.get_settings(args)
    config = settings.config

    logger.update_logger(LOG, config["logging"]["level"], config["logging"]["json"])

    files = config["rules"]["files"]
    standards = base.get_standards(config["rules"]["standards"])

    workers = multiprocessing.cpu_count() - 2
    p = multiprocessing.Pool(workers)
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
            p.imap(candidate.review, (settings, lines,))
        else:
            LOG.info("Couldn't classify file %s" % filename)

    p.close()
    p.join()


if __name__ == "__main__":
    main()
