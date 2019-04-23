"""Checks related to ansible roles files."""

from ansible.parsing.yaml.objects import AnsibleMapping
from nested_lookup import nested_lookup

from ansiblelater.command.candidates import Error
from ansiblelater.command.candidates import Result
from ansiblelater.utils.rulehelper import get_raw_yaml
from ansiblelater.utils.rulehelper import get_tasks


def check_meta_main(candidate, settings):
    content, errors = get_raw_yaml(candidate, settings)
    keys = ["author", "description", "min_ansible_version", "platforms", "dependencies"]
    description = "file should contain '%s' key"

    if not errors:
        for key in keys:
            if not nested_lookup(key, content):
                errors.append(Error(None, description % (key)))

    return Result(candidate.path, errors)


def check_scm_in_src(candidate, settings):
    roles, errors = get_tasks(candidate, settings)
    description = "usage of src: scm+url not recommended"

    if not errors:
        for role in roles:
            if isinstance(role, AnsibleMapping):
                if "+" in role.get("src"):
                    errors.append(Error(role["__line__"], description))

    return Result(candidate.path, errors)
