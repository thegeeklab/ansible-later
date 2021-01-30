#!/usr/bin/env python
"""Main program."""

import argparse
import multiprocessing
import sys

from ansiblelater import LOG
from ansiblelater import __version__
from ansiblelater import logger
from ansiblelater.candidate import Candidate
from ansiblelater.settings import Settings
from ansiblelater.standard import SingleStandards


def main():
    """Run main program."""
    parser = argparse.ArgumentParser(
        description="Validate Ansible files against best practice guideline"
    )
    parser.add_argument(
        "-c", "--config", dest="config_file", metavar="CONFIG", help="path to configuration file"
    )
    parser.add_argument(
        "-r",
        "--rules-dir",
        dest="rules.standards",
        metavar="RULES",
        action="append",
        help="directory of standard rules"
    )
    parser.add_argument(
        "-B",
        "--no-buildin",
        dest="rules.buildin",
        action="store_false",
        help="disables build-in standard rules"
    )
    parser.add_argument(
        "-s",
        "--standards",
        dest="rules.filter",
        metavar="FILTER",
        action="append",
        help="limit standards to given ID's"
    )
    parser.add_argument(
        "-x",
        "--exclude-standards",
        dest="rules.exclude_filter",
        metavar="EXCLUDE_FILTER",
        action="append",
        help="exclude standards by given ID's"
    )
    parser.add_argument(
        "-v", dest="logging.level", action="append_const", const=-1, help="increase log level"
    )
    parser.add_argument(
        "-q", dest="logging.level", action="append_const", const=1, help="decrease log level"
    )
    parser.add_argument("rules.files", nargs="*")
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s {}".format(__version__)
    )

    args = parser.parse_args().__dict__

    settings = Settings(args=args)
    config = settings.config

    logger.update_logger(LOG, config["logging"]["level"], config["logging"]["json"])
    SingleStandards(config["rules"]["standards"]).rules

    workers = max(multiprocessing.cpu_count() - 2, 2)
    p = multiprocessing.Pool(workers)
    tasks = []
    for filename in config["rules"]["files"]:
        candidate = Candidate.classify(filename, settings)
        if candidate:
            if candidate.binary:
                LOG.info("Not reviewing binary file {name}".format(name=filename))
                continue
            if candidate.vault:
                LOG.info("Not reviewing vault file {name}".format(name=filename))
                continue
            else:
                LOG.info("Reviewing all of {candidate}".format(candidate=candidate))
                tasks.append(candidate)
        else:
            LOG.info("Couldn't classify file {name}".format(name=filename))

    errors = (sum(p.map(_review_wrapper, tasks)))
    p.close()
    p.join()

    if not errors == 0:
        return_code = 1
    else:
        return_code = 0

    sys.exit(return_code)


def _review_wrapper(candidate):
    return candidate.review()


if __name__ == "__main__":
    main()
