"""Checks related to ansible specific best practices."""

import os
import re
from collections import defaultdict

from ansiblelater.command.candidates import Error
from ansiblelater.command.candidates import Result
from ansiblelater.command.candidates import Template
from ansiblelater.utils import count_spaces
from ansiblelater.utils.rulehelper import get_first_cmd_arg
from ansiblelater.utils.rulehelper import get_normalized_tasks
from ansiblelater.utils.rulehelper import get_normalized_yaml


def check_braces_spaces(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    conf = settings["ansible"]["double-braces"]
    description = "no suitable numbers of spaces (min: {min} max: {max})".format(
        min=conf["min-spaces-inside"], max=conf["max-spaces-inside"]
    )

    matches = []
    braces = re.compile("{{(.*?)}}")

    if not errors:
        for i, line in yamllines:
            if "!unsafe" in line:
                continue
            match = braces.findall(line)
            if match:
                for item in match:
                    matches.append((i, item))

        for i, line in matches:
            [leading, trailing] = count_spaces(line)
            sum_spaces = leading + trailing

            if (
                sum_spaces < conf["min-spaces-inside"] * 2
                or sum_spaces > conf["min-spaces-inside"] * 2
            ):
                errors.append(Error(i, description))
    return Result(candidate.path, errors)


def check_named_task(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    nameless_tasks = [
        "meta", "debug", "include_role", "import_role", "include_tasks", "import_tasks",
        "include_vars", "block"
    ]
    description = "module '{module}' used without or empty name attribute"

    if not errors:
        for task in tasks:
            module = task["action"]["__ansible_module__"]
            if ("name" not in task or not task["name"]) and module not in nameless_tasks:
                errors.append(Error(task["__line__"], description.format(module=module)))

    return Result(candidate.path, errors)


def check_name_format(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "name '{name}' should start with uppercase"
    namelines = defaultdict(list)

    if not errors:
        for task in tasks:
            if "name" in task:
                namelines[task["name"]].append(task["__line__"])
        for (name, lines) in namelines.items():
            if name and not name[0].isupper():
                errors.append(Error(lines[-1], description.format(name=name)))

    return Result(candidate.path, errors)


def check_unique_named_task(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "name '{name}' appears multiple times"

    namelines = defaultdict(list)

    if not errors:
        for task in tasks:
            if "name" in task:
                namelines[task["name"]].append(task["__line__"])
        for (name, lines) in namelines.items():
            if name and len(lines) > 1:
                errors.append(Error(lines[-1], description.format(name=name)))

    return Result(candidate.path, errors)


def check_command_instead_of_module(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    commands = ["command", "shell", "raw"]
    modules = {
        "git": "git",
        "hg": "hg",
        "curl": "get_url or uri",
        "wget": "get_url or uri",
        "svn": "subversion",
        "service": "service",
        "mount": "mount",
        "rpm": "yum or rpm_key",
        "yum": "yum",
        "apt-get": "apt-get",
        "unzip": "unarchive",
        "tar": "unarchive",
        "chkconfig": "service",
        "rsync": "synchronize",
        "supervisorctl": "supervisorctl",
        "systemctl": "systemd",
        "sed": "template or lineinfile"
    }
    description = "{exec} command used in place of {module} module"

    if not errors:
        for task in tasks:
            if task["action"]["__ansible_module__"] in commands:
                first_cmd_arg = get_first_cmd_arg(task)
                executable = os.path.basename(first_cmd_arg)
                if (
                    first_cmd_arg and executable in modules and task["action"].get("warn", True)
                    and "register" not in task
                ):
                    errors.append(
                        Error(
                            task["__line__"],
                            description.format(exec=executable, module=modules[executable])
                        )
                    )

    return Result(candidate.path, errors)


def check_install_use_latest(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    package_managers = [
        "yum", "apt", "dnf", "homebrew", "pacman", "openbsd_package", "pkg5", "portage", "pkgutil",
        "slackpkg", "swdepot", "zypper", "bundler", "pip", "pear", "npm", "yarn", "gem",
        "easy_install", "bower", "package", "apk", "openbsd_pkg", "pkgng", "sorcery", "xbps"
    ]
    description = "package installs should use state=present with or without a version"

    if not errors:
        for task in tasks:
            if (
                task["action"]["__ansible_module__"] in package_managers
                and task["action"].get("state") == "latest"
            ):
                errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_shell_instead_command(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    description = "shell should only be used when piping, redirecting or chaining commands"

    if not errors:
        for task in tasks:
            if task["action"]["__ansible_module__"] == "shell":
                # skip processing if args.executable is used as this
                # parameter is no longer support by command module
                if "executable" in task["action"]:
                    continue

                if "cmd" in task["action"]:
                    cmd = task["action"].get("cmd", [])
                else:
                    cmd = " ".join(task["action"].get("__ansible_arguments__", []))

                unjinja = re.sub(r"\{\{[^\}]*\}\}", "JINJA_VAR", cmd)
                if not any([ch in unjinja for ch in "&|<>;$\n*[]{}?"]):
                    errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_command_has_changes(candidate, settings):
    tasks, errors = get_normalized_tasks(candidate, settings)
    commands = ["command", "shell", "raw"]
    description = "commands should either read information (and thus set changed_when) or not " \
                  "do something if it has already been done (using creates/removes) " \
                  "or only do it if another check has a particular result (when)"

    if not errors:
        for task in tasks:
            if task["action"]["__ansible_module__"] in commands:
                if (
                    "changed_when" not in task and "when" not in task
                    and "when" not in task.get("__ansible_action_meta__", [])
                    and "creates" not in task["action"] and "removes" not in task["action"]
                ):
                    errors.append(Error(task["__line__"], description))

    return Result(candidate.path, errors)


def check_command_instead_of_argument(candidate, settings):
    # Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.

    tasks, errors = get_normalized_tasks(candidate, settings)
    commands = ["command", "shell", "raw"]
    arguments = {
        "chown": "owner",
        "chmod": "mode",
        "chgrp": "group",
        "ln": "state=link",
        "mkdir": "state=directory",
        "rmdir": "state=absent",
        "rm": "state=absent"
    }
    description = "{exec} used in place of file modules argument {arg}"

    if not errors:
        for task in tasks:
            if task["action"]["__ansible_module__"] in commands:
                first_cmd_arg = get_first_cmd_arg(task)
                executable = os.path.basename(first_cmd_arg)

                if (
                    first_cmd_arg and executable in arguments and task["action"].get("warn", True)
                ):
                    errors.append(
                        Error(
                            task["__line__"],
                            description.format(exec=executable, arg=arguments[executable])
                        )
                    )

    return Result(candidate.path, errors)


def check_empty_string_compare(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    description = "use `when: var` rather than `when: var != ""` (or " \
                  "conversely `when: not var` rather than `when: var == ""`)"

    if not errors:
        if isinstance(candidate, Template):
            matches = []
            jinja_string = re.compile("({{|{%)(.*?)(}}|%})")

            for i, line in yamllines:
                match = jinja_string.findall(line)
                if match:
                    for item in match:
                        matches.append((i, item[1]))

            yamllines = matches

        empty_string_compare = re.compile("[=!]= ?[\"'][\"']")

        for i, line in yamllines:
            if empty_string_compare.findall(line):
                errors.append(Error(i, description))

    return Result(candidate.path, errors)


def check_compare_to_literal_bool(candidate, settings):
    yamllines, errors = get_normalized_yaml(candidate, settings)
    description = "use `when: var` rather than `when: var == True` " \
                  "(or conversely `when: not var`)"

    if not errors:
        if isinstance(candidate, Template):
            matches = []
            jinja_string = re.compile("({{|{%)(.*?)(}}|%})")

            for i, line in yamllines:
                match = jinja_string.findall(line)
                if match:
                    for item in match:
                        matches.append((i, item[1]))

            yamllines = matches

        literal_bool_compare = re.compile("[=!]= ?(True|true|False|false)")

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
            if task.get("delegate_to") == "localhost":
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
    true_value = [True, "true", "True", "TRUE", "yes", "Yes", "YES"]

    if not errors:
        gen = (task for task in tasks if "become" in task)
        for task in gen:
            if task["become"] in true_value and "become_user" not in task.keys():
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
