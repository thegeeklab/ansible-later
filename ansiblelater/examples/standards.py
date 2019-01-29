from ansiblelater import Standard

from ansiblelater.rules.yamlfiles import check_yaml_empty_lines
from ansiblelater.rules.yamlfiles import check_yaml_indent
from ansiblelater.rules.yamlfiles import check_yaml_hyphens
from ansiblelater.rules.yamlfiles import check_yaml_document_start
from ansiblelater.rules.yamlfiles import check_yaml_colons
from ansiblelater.rules.yamlfiles import check_yaml_file
from ansiblelater.rules.yamlfiles import check_yaml_has_content
from ansiblelater.rules.yamlfiles import check_native_yaml
from ansiblelater.rules.taskfiles import check_line_between_tasks
from ansiblelater.rules.rolefiles import check_meta_main
from ansiblelater.rules.rolefiles import check_scm_in_src
from ansiblelater.rules.ansiblefiles import check_unique_named_task
from ansiblelater.rules.ansiblefiles import check_named_task
from ansiblelater.rules.ansiblefiles import check_name_format
from ansiblelater.rules.ansiblefiles import check_braces_spaces
from ansiblelater.rules.ansiblefiles import check_command_instead_of_module
from ansiblelater.rules.ansiblefiles import check_install_use_latest
from ansiblelater.rules.ansiblefiles import check_shell_instead_command
from ansiblelater.rules.ansiblefiles import check_command_has_changes
from ansiblelater.rules.ansiblefiles import check_empty_string_compare
from ansiblelater.rules.ansiblefiles import check_compare_to_literal_bool
from ansiblelater.rules.ansiblefiles import check_literal_bool_format
from ansiblelater.rules.ansiblefiles import check_become_user
from ansiblelater.rules.ansiblefiles import check_filter_separation


tasks_should_be_separated = Standard(dict(
    id="ANSIBLE0001",
    name="Single tasks should be separated by empty line",
    check=check_line_between_tasks,
    version="0.1",
    types=["playbook", "task", "handler"]
))

role_must_contain_meta_main = Standard(dict(
    id="ANSIBLE0002",
    name="Roles must contain suitable meta/main.yml",
    check=check_meta_main,
    version="0.1",
    types=["meta"]
))

tasks_are_uniquely_named = Standard(dict(
    id="ANSIBLE0003",
    name="Tasks and handlers must be uniquely named within a single file",
    check=check_unique_named_task,
    version="0.1",
    types=["playbook", "task", "handler"],
))

use_spaces_between_variable_braces = Standard(dict(
    id="ANSIBLE0004",
    name="YAML should use consistent number of spaces around variables",
    check=check_braces_spaces,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

roles_scm_not_in_src = Standard(dict(
    id="ANSIBLE0005",
    name="Use scm key rather than src: scm+url",
    check=check_scm_in_src,
    version="0.1",
    types=["rolesfile"]
))

tasks_are_named = Standard(dict(
    id="ANSIBLE0006",
    name="Tasks and handlers must be named",
    check=check_named_task,
    version="0.1",
    types=["playbook", "task", "handler"],
))

tasks_names_are_formatted = Standard(dict(
    id="ANSIBLE0007",
    name="Name of tasks and handlers must be formatted",
    check=check_name_format,
    version="0.1",
    types=["playbook", "task", "handler"],
))

commands_should_not_be_used_in_place_of_modules = Standard(dict(
    id="ANSIBLE0008",
    name="Commands should not be used in place of modules",
    check=check_command_instead_of_module,
    version="0.1",
    types=["playbook", "task", "handler"]
))

package_installs_should_not_use_latest = Standard(dict(
    id="ANSIBLE0009",
    name="Package installs should use present, not latest",
    check=check_install_use_latest,
    types=["playbook", "task", "handler"]
))

use_shell_only_when_necessary = Standard(dict(
    id="ANSIBLE0010",
    name="Shell should only be used when essential",
    check=check_shell_instead_command,
    types=["playbook", "task", "handler"]
))

commands_should_be_idempotent = Standard(dict(
    id="ANSIBLE0011",
    name="Commands should be idempotent",
    check=check_command_has_changes,
    version="0.1",
    types=["playbook", "task"]
))

dont_compare_to_empty_string = Standard(dict(
    id="ANSIBLE0012",
    name="Don't compare to \"\" - use `when: var` or `when: not var`",
    check=check_empty_string_compare,
    version="0.1",
    types=["playbook", "task", "handler", "template"]
))

dont_compare_to_literal_bool = Standard(dict(
    id="ANSIBLE0013",
    name="Don't compare to True or False - use `when: var` or `when: not var`",
    check=check_compare_to_literal_bool,
    version="0.1",
    types=["playbook", "task", "handler", "template"]
))

literal_bool_should_be_formatted = Standard(dict(
    id="ANSIBLE0014",
    name="Literal bools should start with a capital letter",
    check=check_literal_bool_format,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars"]
))

use_become_with_become_user = Standard(dict(
    id="ANSIBLE0015",
    name="become should be combined with become_user",
    check=check_become_user,
    version="0.1",
    types=["playbook", "task", "handler"]
))

use_spaces_around_filters = Standard(dict(
    id="ANSIBLE0016",
    name="jinja2 filters should be separated with spaces",
    check=check_filter_separation,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars"]
))

files_should_not_contain_unnecessarily_empty_lines = Standard(dict(
    id="LINT0001",
    name="YAML should not contain unnecessarily empty lines",
    check=check_yaml_empty_lines,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

files_should_be_indented = Standard(dict(
    id="LINT0002",
    name="YAML should be correctly indented",
    check=check_yaml_indent,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

files_should_use_consistent_spaces_after_hyphens = Standard(dict(
    id="LINT0003",
    name="YAML should use consistent number of spaces after hyphens",
    check=check_yaml_hyphens,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

files_should_contain_document_start_marker = Standard(dict(
    id="LINT0004",
    name="YAML should contain document start marker",
    check=check_yaml_document_start,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

spaces_around_colons = Standard(dict(
    id="LINT0005",
    name="YAML should use consistent number of spaces around colons",
    check=check_yaml_colons,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

rolesfile_should_be_in_yaml = Standard(dict(
    id="LINT0006",
    name="Roles file should be in yaml format",
    check=check_yaml_file,
    version="0.1",
    types=["rolesfile"]
))

files_should_not_be_purposeless = Standard(dict(
    id="LINT0007",
    name="Files should contain useful content",
    check=check_yaml_has_content,
    version="0.1",
    types=["playbook", "task", "handler", "rolevars", "defaults", "meta"]
))

use_yaml_rather_than_key_value = Standard(dict(
    id="LINT0008",
    name="Use YAML format for tasks and handlers rather than key=value",
    check=check_native_yaml,
    version="0.1",
    types=["playbook", "task", "handler"]
))


ansible_min_version = '2.1'
ansible_review_min_version = '0.1.0'


standards = [
    # Ansible
    tasks_should_be_separated,
    role_must_contain_meta_main,
    tasks_are_uniquely_named,
    use_spaces_between_variable_braces,
    roles_scm_not_in_src,
    tasks_are_named,
    tasks_names_are_formatted,
    commands_should_not_be_used_in_place_of_modules,
    package_installs_should_not_use_latest,
    use_shell_only_when_necessary,
    commands_should_be_idempotent,
    dont_compare_to_empty_string,
    dont_compare_to_literal_bool,
    literal_bool_should_be_formatted,
    use_become_with_become_user,
    use_spaces_around_filters,
    # Lint
    files_should_not_contain_unnecessarily_empty_lines,
    files_should_be_indented,
    files_should_use_consistent_spaces_after_hyphens,
    files_should_contain_document_start_marker,
    spaces_around_colons,
    rolesfile_should_be_in_yaml,
    files_should_not_be_purposeless,
    use_yaml_rather_than_key_value,
]
