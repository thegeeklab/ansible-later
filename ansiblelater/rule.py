"""Rule definition."""

import copy
import importlib
import inspect
import os
import pathlib
import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from urllib.parse import urlparse

import toolz
import yaml
from yamllint import linter
from yamllint.config import YamlLintConfig

from ansiblelater.exceptions import LaterAnsibleError, LaterError
from ansiblelater.utils import Singleton, sysexit_with_message
from ansiblelater.utils.yamlhelper import (
    UnsafeTag,
    VaultTag,
    action_tasks,
    normalize_task,
    normalized_yaml,
    parse_yaml_linenumbers,
)


class RuleMeta(type):
    def __call__(cls, *args):
        mcls = type.__call__(cls, *args)
        mcls.rid = cls.rid
        mcls.description = getattr(cls, "description", "__unknown__")
        mcls.helptext = getattr(cls, "helptext", "")
        mcls.types = getattr(cls, "types", [])
        return mcls


class RuleExtendedMeta(RuleMeta, ABCMeta):
    pass


class RuleBase(metaclass=RuleExtendedMeta):
    SHELL_PIPE_CHARS = "&|<>;$\n*[]{}?"

    @property
    @abstractmethod
    def rid(self):
        pass

    @abstractmethod
    def check(self, candidate, settings):
        pass

    def __repr__(self):
        return f"Rule: {self.description} (types: {self.types})"

    @staticmethod
    def get_tasks(candidate, settings):  # noqa
        errors = []
        yamllines = []

        if not candidate.faulty:
            try:
                with open(candidate.path, encoding="utf-8") as f:
                    yamllines = parse_yaml_linenumbers(f, candidate.path)
            except LaterError as ex:
                e = ex.original
                errors.append(
                    RuleBase.Error(e.problem_mark.line + 1, f"syntax error: {e.problem}")
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(RuleBase.Error(e.line, f"syntax error: {e.message}"))
                candidate.faulty = True

        return yamllines, errors

    @staticmethod
    def get_action_tasks(candidate, settings):  # noqa
        tasks = []
        errors = []

        if not candidate.faulty:
            try:
                with open(candidate.path, encoding="utf-8") as f:
                    yamllines = parse_yaml_linenumbers(f, candidate.path)

                if yamllines:
                    tasks = action_tasks(yamllines, candidate)
            except LaterError as ex:
                e = ex.original
                errors.append(
                    RuleBase.Error(e.problem_mark.line + 1, f"syntax error: {e.problem}")
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(RuleBase.Error(e.line, f"syntax error: {e.message}"))
                candidate.faulty = True

        return tasks, errors

    @staticmethod
    def get_normalized_task(task, candidate, settings):
        normalized = None
        errors = []

        if not candidate.faulty:
            try:
                normalized = normalize_task(
                    copy.copy(task), candidate.path, settings["ansible"]["custom_modules"]
                )
            except LaterError as ex:
                e = ex.original
                errors.append(
                    RuleBase.Error(e.problem_mark.line + 1, f"syntax error: {e.problem}")
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(RuleBase.Error(e.line, f"syntax error: {e.message}"))
                candidate.faulty = True

        return normalized, errors

    @staticmethod
    def get_normalized_tasks(candidate, settings, full=False):
        normalized = []
        errors = []

        if not candidate.faulty:
            try:
                with open(candidate.path, encoding="utf-8") as f:
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

                        normalized_task = normalize_task(
                            task, candidate.path, settings["ansible"]["custom_modules"]
                        )
                        normalized_task["__raw_task__"] = task

                        normalized.append(normalized_task)

            except LaterError as ex:
                e = ex.original
                errors.append(
                    RuleBase.Error(e.problem_mark.line + 1, f"syntax error: {e.problem}")
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(RuleBase.Error(e.line, f"syntax error: {e.message}"))
                candidate.faulty = True

        return normalized, errors

    @staticmethod
    def get_normalized_yaml(candidate, settings, options=None):  # noqa
        errors = []
        yamllines = []

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
                    RuleBase.Error(e.problem_mark.line + 1, f"syntax error: {e.problem}")
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(RuleBase.Error(e.line, f"syntax error: {e.message}"))
                candidate.faulty = True

        return yamllines, errors

    @staticmethod
    def get_raw_yaml(candidate, settings):  # noqa
        content = None
        errors = []

        if not candidate.faulty:
            try:
                with open(candidate.path, encoding="utf-8") as f:
                    yaml.add_constructor(
                        UnsafeTag.yaml_tag, UnsafeTag.yaml_constructor, Loader=yaml.SafeLoader
                    )
                    yaml.add_constructor(
                        VaultTag.yaml_tag, VaultTag.yaml_constructor, Loader=yaml.SafeLoader
                    )
                    content = yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(
                    RuleBase.Error(e.problem_mark.line + 1, f"syntax error: {e.problem}")
                )
                candidate.faulty = True

        return content, errors

    @staticmethod
    def run_yamllint(candidate, options="extends: default"):
        errors = []

        if not candidate.faulty:
            try:
                with open(candidate.path, encoding="utf-8") as f:
                    for problem in linter.run(f, YamlLintConfig(options)):
                        errors.append(RuleBase.Error(problem.line, problem.desc))
            except yaml.YAMLError as e:
                errors.append(
                    RuleBase.Error(e.problem_mark.line + 1, f"syntax error: {e.problem}")
                )
                candidate.faulty = True
            except (TypeError, ValueError) as e:
                errors.append(RuleBase.Error(None, f"yamllint error: {e}"))
                candidate.faulty = True

        return errors

    @staticmethod
    def get_first_cmd_arg(task):
        if "cmd" in task["action"]:
            first_cmd_arg = task["action"]["cmd"].split()[0]
        elif "argv" in task["action"]:
            first_cmd_arg = task["action"]["argv"][0]
        else:
            first_cmd_arg = task["action"]["__ansible_arguments__"][0]

        return first_cmd_arg

    @staticmethod
    def get_safe_cmd(task):
        if "cmd" in task["action"]:
            cmd = task["action"].get("cmd", "")
        else:
            cmd = " ".join(task["action"].get("__ansible_arguments__", []))

        cmd = re.sub(r"{{.+?}}", "JINJA_EXPRESSION", cmd)
        cmd = re.sub(r"{%.+?%}", "JINJA_STATEMENT", cmd)
        cmd = re.sub(r"{#.+?#}", "JINJA_COMMENT", cmd)

        parts = cmd.split()
        parts = [p if not urlparse(p.strip('"').strip("'")).scheme else "URL" for p in parts]

        return " ".join(parts)

    class Error:
        """Default error object created if a rule failed."""

        def __init__(self, lineno, message, **kwargs):
            """
            Initialize a new error object and returns None.

            :param lineno: Line number where the error from de rule occures
            :param message: Detailed error description provided by the rule

            """
            self.lineno = lineno
            self.message = message
            self.kwargs = kwargs
            for key, value in kwargs.items():
                setattr(self, key, value)

        def __repr__(self):
            if self.lineno:
                return f"{self.lineno}: {self.message}"
            return f" {self.message}"

        def to_dict(self):
            result = {"lineno": self.lineno, "message": self.message}
            for key, value in self.kwargs.items():
                result[key] = value
            return result

    class Result:
        """Generic result object."""

        def __init__(self, candidate, errors=None):
            self.candidate = candidate
            self.errors = errors or []

        def message(self):
            return "\n".join([f"{self.candidate}:{error}" for error in self.errors])


class RulesLoader:
    def __init__(self, source):
        self.rules = []

        for s in source:
            for p in pathlib.Path(s).glob("*.py"):
                filename = os.path.splitext(os.path.basename(p))[0]
                if not re.match(r"^[A-Za-z]+$", filename):
                    continue

                spec = importlib.util.spec_from_file_location(filename, p)
                module = importlib.util.module_from_spec(spec)

                try:
                    spec.loader.exec_module(module)
                except (ImportError, NameError) as e:
                    sysexit_with_message(f"Failed to load roles file {filename}: \n {e!s}")

                try:
                    for _name, obj in inspect.getmembers(module):
                        if self._is_plugin(obj):
                            self.rules.append(obj())
                except TypeError as e:
                    sysexit_with_message(f"Failed to load roles file: \n {e!s}")

        self.validate()

    def _is_plugin(self, obj):
        return (
            inspect.isclass(obj) and issubclass(obj, RuleBase) and obj is not RuleBase and not None
        )

    def validate(self):
        normalize_rule = list(toolz.remove(lambda x: x.rid == "", self.rules))
        unique_rule = len(list(toolz.unique(normalize_rule, key=lambda x: x.rid)))
        all_rules = len(normalize_rule)
        if all_rules != unique_rule:
            sysexit_with_message(
                "Found duplicate tags in rules definition. Please use unique tags only."
            )


class SingleRules(RulesLoader, metaclass=Singleton):
    """Singleton config class."""

    pass
