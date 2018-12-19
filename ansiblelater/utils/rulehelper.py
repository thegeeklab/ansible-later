import codecs
import yaml

from collections import defaultdict
from yamllint import linter
from yamllint.config import YamlLintConfig
# Workaround for import errors with ansble 2.1 and 2.3
from ansible.parsing.dataloader import DataLoader
from ansiblelater import Error
from .yamlhelper import normalize_task
from .yamlhelper import action_tasks
from .yamlhelper import parse_yaml_linenumbers
from .yamlhelper import normalized_yaml
from .exceptions import LaterError, LaterAnsibleError


def get_tasks(candidate, settings):
    errors = []
    try:
        with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
            yamllines = parse_yaml_linenumbers(f, candidate.path)

    except LaterError as ex:
        e = ex.original
        errors.append(Error(e.problem_mark.line + 1, "syntax error: %s" % (e.problem)))
    except LaterAnsibleError as e:
        errors.append(Error(e.line, "syntax error: %s" % (e.message)))

    return yamllines, errors


def get_action_tasks(candidate, settings):
    tasks = []
    errors = []
    try:
        with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
            yamllines = parse_yaml_linenumbers(f, candidate.path)

        if yamllines:
            tasks = action_tasks(yamllines, candidate)
    except LaterError as ex:
        e = ex.original
        errors.append(Error(e.problem_mark.line + 1, "syntax error: %s" % (e.problem)))
    except LaterAnsibleError as e:
        errors.append(Error(e.line, "syntax error: %s" % (e.message)))

    return tasks, errors


def get_normalized_task(task, candidate, settings):
    normalized = None
    errors = []
    try:
        normalized = normalize_task(task, candidate.path, settings.custom_modules)
    except LaterError as ex:
        e = ex.original
        errors.append(Error(e.problem_mark.line + 1, "syntax error: %s" % (e.problem)))
    except LaterAnsibleError as e:
        errors.append(Error(e.line, "syntax error: %s" % (e.message)))

    return normalized, errors


def get_normalized_tasks(candidate, settings):
    normalized = []
    errors = []
    try:
        with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
            yamllines = parse_yaml_linenumbers(f, candidate.path)

        if yamllines:
            tasks = action_tasks(yamllines, candidate)
            for task in tasks:
                # An empty `tags` block causes `None` to be returned if
                # the `or []` is not present - `task.get('tags', [])`
                # does not suffice.
                if 'skip_ansible_lint' in (task.get('tags') or []):
                    # No need to normalize_task if we are skipping it.
                    continue
                normalized.append(normalize_task(task, candidate.path, settings.custom_modules))

    except LaterError as ex:
        e = ex.original
        errors.append(Error(e.problem_mark.line + 1, "syntax error: %s" % (e.problem)))
    except LaterAnsibleError as e:
        errors.append(Error(e.line, "syntax error: %s" % (e.message)))

    return normalized, errors


def get_normalized_yaml(candidate, settings, options=None):
    errors = []

    if not options:
        options = defaultdict(dict)
        options.update(remove_empty=True)
        options.update(remove_markers=True)

    try:
        yamllines = normalized_yaml(candidate.path, options)
    except LaterError as ex:
        e = ex.original
        errors.append(Error(e.problem_mark.line + 1, "syntax error: %s" % (e.problem)))
    except LaterAnsibleError as e:
        errors.append(Error(e.line, "syntax error: %s" % (e.message)))

    return yamllines, errors


def get_raw_yaml(candidate, settings):
    content = None
    errors = []

    try:
        with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
            content = yaml.safe_load(f)

    except LaterError as ex:
        e = ex.original
        errors.append(Error(e.problem_mark.line + 1, "syntax error: %s" % (e.problem)))

    return content, errors


def run_yamllint(candidate, settings, options="extends: default"):
    errors = []
    try:
        with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
            for problem in linter.run(f, YamlLintConfig(options)):
                errors.append(Error(problem.line, problem.desc))
    except LaterError as ex:
        e = ex.original
        errors.append(Error(e.problem_mark.line + 1, "syntax error: %s" % (e.problem)))

    return errors
