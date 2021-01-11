"""Abstracted methods to simplify role writeup."""

import codecs
from collections import defaultdict

import yaml
from yamllint import linter
from yamllint.config import YamlLintConfig

from ansiblelater.command.candidates import Error
from ansiblelater.exceptions import LaterAnsibleError
from ansiblelater.exceptions import LaterError

from .yamlhelper import UnsafeTag
from .yamlhelper import action_tasks
from .yamlhelper import normalize_task
from .yamlhelper import normalized_yaml
from .yamlhelper import parse_yaml_linenumbers


def get_tasks(candidate, settings):
    errors = []
    yamllines = []

    if not candidate.faulty:
        try:
            with codecs.open(candidate.path, mode="rb", encoding="utf-8") as f:
                yamllines = parse_yaml_linenumbers(f, candidate.path)
        except LaterError as ex:
            e = ex.original
            errors.append(
                Error(e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem))
            )
            candidate.faulty = True
        except LaterAnsibleError as e:
            errors.append(Error(e.line, "syntax error: {msg}".format(msg=e.message)))
            candidate.faulty = True

    return yamllines, errors


def get_action_tasks(candidate, settings):
    tasks = []
    errors = []

    if not candidate.faulty:
        try:
            with codecs.open(candidate.path, mode="rb", encoding="utf-8") as f:
                yamllines = parse_yaml_linenumbers(f, candidate.path)

            if yamllines:
                tasks = action_tasks(yamllines, candidate)
        except LaterError as ex:
            e = ex.original
            errors.append(
                Error(e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem))
            )
            candidate.faulty = True
        except LaterAnsibleError as e:
            errors.append(Error(e.line, "syntax error: {}".format(e.message)))
            candidate.faulty = True

    return tasks, errors


def get_normalized_task(task, candidate, settings):
    normalized = None
    errors = []

    if not candidate.faulty:
        try:
            normalized = normalize_task(
                task, candidate.path, settings["ansible"]["custom_modules"]
            )
        except LaterError as ex:
            e = ex.original
            errors.append(
                Error(e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem))
            )
            candidate.faulty = True
        except LaterAnsibleError as e:
            errors.append(Error(e.line, "syntax error: {msg}".format(msg=e.message)))
            candidate.faulty = True

    return normalized, errors


def get_normalized_tasks(candidate, settings, full=False):
    normalized = []
    errors = []

    if candidate.faulty:
        try:
            with codecs.open(candidate.path, mode="rb", encoding="utf-8") as f:
                yamllines = parse_yaml_linenumbers(f, candidate.path)

            if yamllines:
                tasks = action_tasks(yamllines, candidate)
                for task in tasks:
                    # An empty `tags` block causes `None` to be returned if
                    # the `or []` is not present - `task.get("tags", [])`
                    # does not suffice.

                    # Deprecated.
                    if "skip_ansible_lint" in (task.get("tags") or []) and not full:
                        # No need to normalize_task if we are skipping it.
                        continue

                    if "skip_ansible_later" in (task.get("tags") or []) and not full:
                        # No need to normalize_task if we are skipping it.
                        continue

                    normalized.append(
                        normalize_task(
                            task, candidate.path, settings["ansible"]["custom_modules"]
                        )
                    )

        except LaterError as ex:
            e = ex.original
            errors.append(
                Error(e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem))
            )
            candidate.faulty = True
        except LaterAnsibleError as e:
            errors.append(Error(e.line, "syntax error: {msg}".format(msg=e.message)))
            candidate.faulty = True

    return normalized, errors


def get_normalized_yaml(candidate, settings, options=None):
    errors = []
    yamllines = None

    if not candidate.faulty:
        if not options:
            options = defaultdict(dict)
            options.update(remove_empty=True)
            options.update(remove_markers=True)

        try:
            yamllines = normalized_yaml(candidate.path, options)
        except LaterError as ex:
            e = ex.original
            errors.append(
                Error(e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem))
            )
            candidate.faulty = True
        except LaterAnsibleError as e:
            errors.append(Error(e.line, "syntax error: {msg}".format(msg=e.message)))
            candidate.faulty = True

    return yamllines, errors


def get_raw_yaml(candidate, settings):
    content = None
    errors = []

    if not candidate.faulty:
        try:
            with codecs.open(candidate.path, mode="rb", encoding="utf-8") as f:
                yaml.add_constructor(
                    UnsafeTag.yaml_tag, UnsafeTag.yaml_constructor, Loader=yaml.SafeLoader
                )
                content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(
                Error(e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem))
            )
            candidate.faulty = True

    return content, errors


def run_yamllint(candidate, options="extends: default"):
    errors = []

    if not candidate.faulty:
        try:
            with codecs.open(candidate.path, mode="rb", encoding="utf-8") as f:
                yaml.add_constructor(
                    UnsafeTag.yaml_tag, UnsafeTag.yaml_constructor, Loader=yaml.SafeLoader
                )
                yaml.safe_load(f)

                for problem in linter.run(f, YamlLintConfig(options)):
                    errors.append(Error(problem.line, problem.desc))
        except yaml.YAMLError as e:
            errors.append(
                Error(e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem))
            )
            candidate.faulty = True

    return errors
