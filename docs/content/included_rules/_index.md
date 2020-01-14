---
title: Included rules
---

Reviews are nothing without some rules or standards against which to review. ansible-later
comes with a couple of built-in checks explained in the following table.

| Rule                            | ID          | Description                                                       | Parameter                                                            |
|---------------------------------|-------------|-------------------------------------------------------------------|----------------------------------------------------------------------|
| check_yaml_empty_lines          | LINT0001    | YAML should not contain unnecessarily empty lines.                | {max: 1, max-start: 0, max-end: 1}                                   |
| check_yaml_indent               | LINT0002    | YAML should be correctly indented.                                | {spaces: 2, check-multi-line-strings: false, indent-sequences: true} |
| check_yaml_hyphens              | LINT0003    | YAML should use consitent number of spaces after hyphens (-).     | {max-spaces-after: 1}                                                |
| check_yaml_document_start       | LINT0004    | YAML should contain document start marker.                        | {document-start: {present: true}}                                    |
| check_yaml_colons               | LINT0005    | YAML should use consitent number of spaces around colons.         | {colons: {max-spaces-before: 0, max-spaces-after: 1}}                |
| check_yaml_file                 | LINT0006    | Roles file should be in yaml format.                              |                                                                      |
| check_yaml_has_content          | LINT0007    | Files should contain useful content.                              |                                                                      |
| check_native_yaml               | LINT0008    | Use YAML format for tasks and handlers rather than key=value.     |                                                                      |
| check_yaml_document_end         | LINT0009    | YAML should contain document end marker.                          | {document-end: {present: true}}                                      |
| check_line_between_tasks        | ANSIBLE0001 | Single tasks should be separated by an empty line.                |                                                                      |
| check_meta_main                 | ANSIBLE0002 | Meta file should contain a basic subset of parameters.            | author, description, min_ansible_version, platforms, dependencies    |
| check_unique_named_task         | ANSIBLE0003 | Tasks and handlers must be uniquely named within a file.          |                                                                      |
| check_braces                    | ANSIBLE0004 | YAML should use consitent number of spaces around variables.      |                                                                      |
| check_scm_in_src                | ANSIBLE0005 | Use scm key rather than src: scm+url in requirements file.        |                                                                      |
| check_named_task                | ANSIBLE0006 | Tasks and handlers must be named.                                 | excludes: meta, debug, include\_\*, import\_\*, block                |
| check_name_format               | ANSIBLE0007 | Name of tasks and handlers must be formatted.                     | formats: first letter capital                                        |
| check_command_instead_of_module | ANSIBLE0008 | Commands should not be used in place of modules.                  |                                                                      |
| check_install_use_latest        | ANSIBLE0009 | Package managers should not install with state=latest.            |                                                                      |
| check_shell_instead_command     | ANSIBLE0010 | Use Shell only when piping, redirecting or chaining commands.     |                                                                      |
| check_command_has_changes       | ANSIBLE0011 | Commands should be idempotent and only used with some checks.     |                                                                      |
| check_empty_string_compare      | ANSIBLE0012 | Don't compare to "" - use `when: var` or `when: not var`.         |                                                                      |
| check_compare_to_literal_bool   | ANSIBLE0013 | Don't compare to True/False - use `when: var` or `when: not var`. |                                                                      |
| check_literal_bool_format       | ANSIBLE0014 | Literal bools should be written as `True/False` or `yes/no`.      | forbidden values are `true false TRUE FALSE Yes No YES NO`           |
| check_become_user               | ANSIBLE0015 | `become` should be always used combined with `become_user`.       |                                                                      |
| check_filter_separation         | ANSIBLE0016 | Jinja2 filters should be separated with spaces.                   |                                                                      |
