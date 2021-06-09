"""Standard definition."""

import codecs
import copy
import importlib
import inspect
import os
import pathlib
import re
from abc import ABCMeta
from abc import abstractmethod
from collections import defaultdict

import toolz
import yaml
from yamllint import linter
from yamllint.config import YamlLintConfig

from ansiblelater.exceptions import LaterAnsibleError
from ansiblelater.exceptions import LaterError
from ansiblelater.utils import Singleton
from ansiblelater.utils import sysexit_with_message
from ansiblelater.utils.yamlhelper import UnsafeTag
from ansiblelater.utils.yamlhelper import VaultTag
from ansiblelater.utils.yamlhelper import action_tasks
from ansiblelater.utils.yamlhelper import normalize_task
from ansiblelater.utils.yamlhelper import normalized_yaml
from ansiblelater.utils.yamlhelper import parse_yaml_linenumbers


class StandardMeta(type):

    def __call__(cls, *args, **kwargs):
        mcls = type.__call__(cls, *args)
        setattr(mcls, "sid", cls.sid)
        setattr(mcls, "description", getattr(cls, "description", "__unknown__"))
        setattr(mcls, "helptext", getattr(cls, "helptext", ""))
        setattr(mcls, "version", getattr(cls, "version", None))
        setattr(mcls, "types", getattr(cls, "types", []))
        return mcls


class StandardExtendedMeta(StandardMeta, ABCMeta):
    pass


class StandardBase(object, metaclass=StandardExtendedMeta):

    @property
    @abstractmethod
    def sid(self):
        pass

    @abstractmethod
    def check(self, candidate, settings):
        pass

    def __repr__(self):  # noqa
        return "Standard: {description} (version: {version}, types: {types})".format(
            description=self.description, version=self.version, types=self.types
        )

    @staticmethod
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
                    StandardBase.Error(
                        e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem)
                    )
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(
                    StandardBase.Error(e.line, "syntax error: {msg}".format(msg=e.message))
                )
                candidate.faulty = True

        return yamllines, errors

    @staticmethod
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
                    StandardBase.Error(
                        e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem)
                    )
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(StandardBase.Error(e.line, "syntax error: {}".format(e.message)))
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
                    StandardBase.Error(
                        e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem)
                    )
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(
                    StandardBase.Error(e.line, "syntax error: {msg}".format(msg=e.message))
                )
                candidate.faulty = True

        return normalized, errors

    @staticmethod
    def get_normalized_tasks(candidate, settings, full=False):
        normalized = []
        errors = []

        if not candidate.faulty:
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
                    StandardBase.Error(
                        e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem)
                    )
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(
                    StandardBase.Error(e.line, "syntax error: {msg}".format(msg=e.message))
                )
                candidate.faulty = True

        return normalized, errors

    @staticmethod
    def get_normalized_yaml(candidate, settings, options=None):
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
                    StandardBase.Error(
                        e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem)
                    )
                )
                candidate.faulty = True
            except LaterAnsibleError as e:
                errors.append(
                    StandardBase.Error(e.line, "syntax error: {msg}".format(msg=e.message))
                )
                candidate.faulty = True

        return yamllines, errors

    @staticmethod
    def get_raw_yaml(candidate, settings):
        content = None
        errors = []

        if not candidate.faulty:
            try:
                with codecs.open(candidate.path, mode="rb", encoding="utf-8") as f:
                    yaml.add_constructor(
                        UnsafeTag.yaml_tag, UnsafeTag.yaml_constructor, Loader=yaml.SafeLoader
                    )
                    yaml.add_constructor(
                        VaultTag.yaml_tag, VaultTag.yaml_constructor, Loader=yaml.SafeLoader
                    )
                    content = yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(
                    StandardBase.Error(
                        e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem)
                    )
                )
                candidate.faulty = True

        return content, errors

    @staticmethod
    def run_yamllint(candidate, options="extends: default"):
        errors = []

        if not candidate.faulty:
            try:
                with codecs.open(candidate.path, mode="rb", encoding="utf-8") as f:
                    for problem in linter.run(f, YamlLintConfig(options)):
                        errors.append(StandardBase.Error(problem.line, problem.desc))
            except yaml.YAMLError as e:
                errors.append(
                    StandardBase.Error(
                        e.problem_mark.line + 1, "syntax error: {msg}".format(msg=e.problem)
                    )
                )
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

    class Error(object):
        """Default error object created if a rule failed."""

        def __init__(self, lineno, message, error_type=None, **kwargs):
            """
            Initialize a new error object and returns None.

            :param lineno: Line number where the error from de rule occures
            :param message: Detailed error description provided by the rule

            """
            self.lineno = lineno
            self.message = message
            self.kwargs = kwargs
            for (key, value) in kwargs.items():
                setattr(self, key, value)

        def __repr__(self):  # noqa
            if self.lineno:
                return "{no}: {msg}".format(no=self.lineno, msg=self.message)
            else:
                return " {msg}".format(msg=self.message)

        def to_dict(self):
            result = dict(lineno=self.lineno, message=self.message)
            for (key, value) in self.kwargs.items():
                result[key] = value
            return result

    class Result(object):
        """Generic result object."""

        def __init__(self, candidate, errors=None):
            self.candidate = candidate
            self.errors = errors or []

        def message(self):
            return "\n".join(["{0}:{1}".format(self.candidate, error) for error in self.errors])


class StandardLoader():

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
                    sysexit_with_message(
                        "Failed to load roles file {module}: \n {msg}".format(
                            msg=str(e), module=filename
                        )
                    )

                try:
                    for name, obj in inspect.getmembers(module):
                        if self._is_plugin(obj):
                            self.rules.append(obj())
                except TypeError as e:
                    sysexit_with_message("Failed to load roles file: \n {msg}".format(msg=str(e)))

        self.validate()

    def _is_plugin(self, obj):
        return inspect.isclass(obj) and issubclass(
            obj, StandardBase
        ) and obj is not StandardBase and not None

    def validate(self):
        normalized_std = (list(toolz.remove(lambda x: x.sid == "", self.rules)))
        unique_std = len(list(toolz.unique(normalized_std, key=lambda x: x.sid)))
        all_std = len(normalized_std)
        if not all_std == unique_std:
            sysexit_with_message(
                "Detect duplicate ID's in standards definition. Please use unique ID's only."
            )


class SingleStandards(StandardLoader, metaclass=Singleton):
    """Singleton config class."""

    pass
