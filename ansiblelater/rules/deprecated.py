"""Checks related to ansible specific best practices."""

from ansiblelater.command.candidates import Error
from ansiblelater.command.candidates import Result
from ansiblelater.utils.rulehelper import get_normalized_tasks


def check_deprecated(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings, full=True)
    description = "'{old}' is deprecated and should not be used anymore. Use '{new}' instead."

    if not errors:
        for task in tasks:
            if "skip_ansible_lint" in (task.get("tags") or []):
                errors.append(
                    Error(
                        task["__line__"],
                        description.format(old="skip_ansible_lint", new="skip_ansible_later")
                    )
                )
    return Result(candidate.path, errors)
