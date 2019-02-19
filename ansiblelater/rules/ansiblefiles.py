import re
import os

from collections import defaultdict
from ansiblelater import Result, Error
from ansiblelater.utils import count_spaces
from ansiblelater.utils.rulehelper import (get_normalized_tasks,
                                           get_normalized_yaml)


def check_braces_spaces(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    description = "no suitable numbers of spaces (required: 1)"

    matches = []
    braces = re.compile("{{(.*?)}}")

    if not errors:
        for i, line in yamllines:
            match = braces.findall(line)
            if match:
                for item in match:
                    matches.append((i, item))

        for i, line in matches:
            leading, trailing = count_spaces(line)

            if not leading == 1 or not trailing == 1:
                errors.append(Error(i, description))
    return Result(candidate.path, errors)


def check_named_task(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    nameless_tasks = ['meta', 'debug', 'include_role', 'import_role',
                      'include_tasks', 'import_tasks', 'include_vars',
                      'block']
    description = "module '%s' used without name attribute"

    if not errors:
        for task in tasks:
            module = task["action"]["__ansible_module__"]
            if 'name' not in task and module not in nameless_tasks:
                errors.append(Error(task['__line__'], description % module))

    return Result(candidate.path, errors)


def check_name_format(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "name '%s' should start with uppercase"
    namelines = defaultdict(list)

    if not errors:
        for task in tasks:
            if 'name' in task:
                namelines[task['name']].append(task['__line__'])
        for (name, lines) in namelines.items():
            if not name[0].isupper():
                errors.append(Error(lines[-1], description % name))

    return Result(candidate.path, errors)


def check_unique_named_task(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "name '%s' appears multiple times"

    namelines = defaultdict(list)

    if not errors:
        for task in tasks:
            if 'name' in task:
                namelines[task['name']].append(task['__line__'])
        for (name, lines) in namelines.items():
            if len(lines) > 1:
                errors.append(Error(lines[-1], description % name))

    return Result(candidate.path, errors)


def check_command_instead_of_module(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    commands = ['command', 'shell', 'raw']
    modules = {
        'git': 'git', 'hg': 'hg', 'curl': 'get_url or uri', 'wget': 'get_url or uri',
        'svn': 'subversion', 'service': 'service', 'mount': 'mount',
        'rpm': 'yum or rpm_key', 'yum': 'yum', 'apt-get': 'apt-get',
        'unzip': 'unarchive', 'tar': 'unarchive', 'chkconfig': 'service',
        'rsync': 'synchronize', 'supervisorctl': 'supervisorctl', 'systemctl': 'systemd',
        'sed': 'template or lineinfile'
    }
    description = "%s command used in place of %s module"

    if not errors:
        for task in tasks:
            if task["action"]["__ansible_module__"] in commands:
                if 'cmd' in task['action']:
                    first_cmd_arg = task["action"]["cmd"].split()[0]
                else:
                    first_cmd_arg = task["action"]["__ansible_arguments__"][0]

                executable = os.path.basename(first_cmd_arg)
                if (first_cmd_arg and executable in modules
                        and task['action'].get('warn', True) and 'register' not in task):
                    errors.append(
                        Error(task["__line__"], description % (executable, modules[executable])))

    return Result(candidate.path, errors)


def check_install_use_latest(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    package_managers = ['yum', 'apt', 'dnf', 'homebrew', 'pacman', 'openbsd_package', 'pkg5',
                        'portage', 'pkgutil', 'slackpkg', 'swdepot', 'zypper', 'bundler', 'pip',
                        'pear', 'npm', 'yarn', 'gem', 'easy_install', 'bower', 'package', 'apk',
                        'openbsd_pkg', 'pkgng', 'sorcery', 'xbps']
    description = "package installs should use state=present with or without a version"

    if not errors:
        for task in tasks:
            if (task["action"]["__ansible_module__"] in package_managers
                    and task["action"].get("state") == "latest"):
                errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_shell_instead_command(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "shell should only be used when piping, redirecting or chaining commands"

    if not errors:
        for task in tasks:
            if task["action"]["__ansible_module__"] == 'shell':
                if 'cmd' in task['action']:
                    cmd = task["action"].get("cmd", [])
                else:
                    cmd = ' '.join(task["action"].get("__ansible_arguments__", []))

                unjinja = re.sub(r"\{\{[^\}]*\}\}", "JINJA_VAR", cmd)
                if not any([ch in unjinja for ch in '&|<>;$\n*[]{}?']):
                    errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_command_has_changes(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    commands = ['command', 'shell', 'raw']
    description = "commands should either read information (and thus set changed_when) or not " \
                  "do something if it has already been done (using creates/removes) " \
                  "or only do it if another check has a particular result (when)"

    if not errors:
        for task in tasks:
            if task["action"]["__ansible_module__"] in commands:
                if ('changed_when' not in task and 'when' not in task
                        and 'when' not in task['__ansible_action_meta__']
                        and 'creates' not in task['action']
                        and 'removes' not in task['action']):
                    errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_empty_string_compare(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    description = 'use `when: var` rather than `when: var != ""` (or ' \
                  'conversely `when: not var` rather than `when: var == ""`)'

    empty_string_compare = re.compile("[=!]= ?[\"'][\"']")

    if not errors:
        for i, line in yamllines:
            if empty_string_compare.findall(line):
                errors.append(Error(i, description))

    return Result(candidate.path, errors)


def check_compare_to_literal_bool(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    description = "use `when: var` rather than `when: var == True` " \
                  "(or conversely `when: not var`)"

    literal_bool_compare = re.compile("[=!]= ?(True|true|False|false)")

    if not errors:
        for i, line in yamllines:
            if literal_bool_compare.findall(line):
                errors.append(Error(i, description))

    return Result(candidate.path, errors)


def check_delegate_to_localhost(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "connection: local ensures that unexpected delegated_vars " \
                  "don't get set (e.g. {{ inventory_hostname }} " \
                  "used by vars_files)"

    if not errors:
        for task in tasks:
            if task.get('delegate_to') == 'localhost':
                errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_literal_bool_format(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    description = "literal bools should be written as 'True/False' or 'yes/no'"

    uppercase_bool = re.compile(r"([=!]=|:)\s*(true|false|TRUE|FALSE|Yes|No|YES|NO)\s*$")

    if not errors:
        for i, line in yamllines:
            if uppercase_bool.findall(line):
                errors.append(Error(i, description))

    return Result(candidate.path, errors)


def check_become_user(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "the task has 'become:' enabled but 'become_user:' is missing"
    true_value = [True, 'true', 'True', 'TRUE', 'yes', 'Yes', 'YES']

    if not errors:
        gen = (task for task in tasks if 'become' in task)
        for task in gen:
            if task["become"] in true_value and 'become_user' not in task.keys():
                errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_filter_separation(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    description = "no suitable numbers of spaces (required: 1)"

    matches = []
    braces = re.compile("{{(.*?)}}")
    filters = re.compile(r"(?<=\|)([\s]{2,}[^\s}]+|[^\s]+)|([^\s{]+[\s]{2,}|[^\s]+)(?=\|)")

    if not errors:
        for i, line in yamllines:
            match = braces.findall(line)
            if match:
                for item in match:
                    matches.append((i, item))

        for i, line in matches:
            if filters.findall(line):
                errors.append(Error(i, description))
    return Result(candidate.path, errors)
