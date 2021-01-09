"""Checks related to generic YAML syntax (yamllint)."""

import os

from ansiblelater.command.candidates import Error
from ansiblelater.command.candidates import Result
from ansiblelater.utils.rulehelper import get_action_tasks
from ansiblelater.utils.rulehelper import get_normalized_task
from ansiblelater.utils.rulehelper import get_normalized_yaml
from ansiblelater.utils.rulehelper import get_raw_yaml
from ansiblelater.utils.rulehelper import run_yamllint


def check_yaml_has_content(candidate, settings):
    lines, errors = get_normalized_yaml(candidate, settings)
    description = "the file appears to have no useful content"

    if (lines and len(lines) == 0) and not errors:
        errors.append(Error(None, description))

    return Result(candidate.path, errors)


def check_native_yaml(candidate, settings):
    tasks, errors = get_action_tasks(candidate, settings)
    description = "task arguments appear to be in key value rather than YAML format"

    if not errors:
        for task in tasks:
            normal_form, error = get_normalized_task(task, candidate, settings)
            if error:
                errors.extend(error)
                break

            action = normal_form["action"]["__ansible_module__"]
            arguments = [
                bytes(x, "utf-8").decode("unicode_escape")
                for x in normal_form["action"]["__ansible_arguments__"]
            ]
            # Cope with `set_fact` where task["set_fact"] is None
            if not task.get(action):
                continue
            if isinstance(task[action], dict):
                continue
            # strip additional newlines off task[action]
            task_action = bytes(task[action].strip(), "utf-8").decode("unicode_escape")
            if task_action.split() != arguments:
                errors.append(Error(task["__line__"], description))
    return Result(candidate.path, errors)


def check_yaml_empty_lines(candidate, settings):
    options = "rules: {{empty-lines: {conf}}}".format(conf=settings["yamllint"]["empty-lines"])
    errors = run_yamllint(candidate, options)
    return Result(candidate.path, errors)


def check_yaml_indent(candidate, settings):
    options = "rules: {{indentation: {conf}}}".format(conf=settings["yamllint"]["indentation"])
    errors = run_yamllint(candidate, options)
    return Result(candidate.path, errors)


def check_yaml_hyphens(candidate, settings):
    options = "rules: {{hyphens: {conf}}}".format(conf=settings["yamllint"]["hyphens"])
    errors = run_yamllint(candidate, options)
    return Result(candidate.path, errors)


def check_yaml_document_start(candidate, settings):
    options = "rules: {{document-start: {conf}}}".format(
        conf=settings["yamllint"]["document-start"]
    )
    errors = run_yamllint(candidate, options)
    return Result(candidate.path, errors)


def check_yaml_document_end(candidate, settings):
    options = "rules: {{document-end: {conf}}}".format(conf=settings["yamllint"]["document-end"])
    errors = run_yamllint(candidate, options)
    return Result(candidate.path, errors)


def check_yaml_colons(candidate, settings):
    options = "rules: {{colons: {conf}}}".format(conf=settings["yamllint"]["colons"])
    errors = run_yamllint(candidate, options)
    return Result(candidate.path, errors)


def check_yaml_file(candidate, settings):
    errors = []
    filename = candidate.path

    if os.path.isfile(filename) and os.path.splitext(filename)[1][1:] != "yml":
        errors.append(Error(None, "file does not have a .yml extension"))
    elif os.path.isfile(filename) and os.path.splitext(filename)[1][1:] == "yml":
        content, errors = get_raw_yaml(candidate, settings)

    return Result(candidate.path, errors)
