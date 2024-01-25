#!/usr/bin/env python
"""Main program."""

import argparse
import multiprocessing
import sys

from ansiblelater import LOG, __version__, logger
from ansiblelater.candidate import Candidate
from ansiblelater.rule import SingleRules
from ansiblelater.settings import Settings


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
        dest="rules.dir",
        metavar="DIR",
        action="append",
        help="directory of rules",
    )
    parser.add_argument(
        "-B",
        "--no-builtin",
        dest="rules.builtin",
        action="store_false",
        help="disables built-in rules",
    )
    parser.add_argument(
        "-i",
        "--include-rules",
        dest="rules.include_filter",
        metavar="TAGS",
        action="append",
        help="limit rules to given id/tags",
    )
    parser.add_argument(
        "-x",
        "--exclude-rules",
        dest="rules.exclude_filter",
        metavar="TAGS",
        action="append",
        help="exclude rules by given it/tags",
    )
    parser.add_argument(
        "-v", dest="logging.level", action="append_const", const=-1, help="increase log level"
    )
    parser.add_argument(
        "-q", dest="logging.level", action="append_const", const=1, help="decrease log level"
    )
    parser.add_argument("rules.files", nargs="*")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args().__dict__

    settings = Settings(args=args)
    config = settings.config

    logger.update_logger(LOG, config["logging"]["level"], config["logging"]["json"])
    SingleRules(config["rules"]["dir"])

    workers = max(multiprocessing.cpu_count() - 2, 2)
    p = multiprocessing.Pool(workers)
    tasks = []
    for filename in config["rules"]["files"]:
        candidate = Candidate.classify(filename, settings)
        if candidate:
            if candidate.binary:
                LOG.info(f"Not reviewing binary file {filename}")
                continue
            if candidate.vault:
                LOG.info(f"Not reviewing vault file {filename}")
                continue

            LOG.info(f"Reviewing all of {candidate}")
            tasks.append(candidate)
        else:
            LOG.info(f"Couldn't classify file {filename}")

    errors = sum(p.map(_review_wrapper, tasks))
    p.close()
    p.join()

    return_code = 1 if errors != 0 else 0

    sys.exit(return_code)


def _review_wrapper(candidate):
    return candidate.review()


if __name__ == "__main__":
    main()
