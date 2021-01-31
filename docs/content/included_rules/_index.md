---
title: Included rules
---

Reviews are nothing without some rules or standards against which to review. ansible-later comes with a couple of built-in checks explained in the following table.

| Rule                          | ID          | Description                                                       | Parameter                                                            |
| ----------------------------- | ----------- | ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| CheckYamlEmptyLines           | LINT0001    | YAML should not contain unnecessarily empty lines.                | {max: 1, max-start: 0, max-end: 1}                                   |
| CheckYamlIndent               | LINT0002    | YAML should be correctly indented.                                | {spaces: 2, check-multi-line-strings: false, indent-sequences: true} |
| CheckYamlHyphens              | LINT0003    | YAML should use consitent number of spaces after hyphens (-).     | {max-spaces-after: 1}                                                |
| CheckYamlDocumentStart        | LINT0004    | YAML should contain document start marker.                        | {document-start: {present: true}}                                    |
| CheckYamlColons               | LINT0005    | YAML should use consitent number of spaces around colons.         | {colons: {max-spaces-before: 0, max-spaces-after: 1}}                |
| CheckYamlFile                 | LINT0006    | Roles file should be in yaml format.                              |                                                                      |
| CheckYamlHasContent           | LINT0007    | Files should contain useful content.                              |                                                                      |
| CheckNativeYaml               | LINT0008    | Use YAML format for tasks and handlers rather than key=value.     |                                                                      |
| CheckYamlDocumentEnd          | LINT0009    | YAML should contain document end marker.                          | {document-end: {present: true}}                                      |
| CheckLineBetweenTasks         | ANSIBLE0001 | Single tasks should be separated by an empty line.                |                                                                      |
| CheckMetaMain                 | ANSIBLE0002 | Meta file should contain a basic subset of parameters.            | author, description, min_ansible_version, platforms, dependencies    |
| CheckUniqueNamedTask          | ANSIBLE0003 | Tasks and handlers must be uniquely named within a file.          |                                                                      |
| CheckBraces                   | ANSIBLE0004 | YAML should use consitent number of spaces around variables.      |                                                                      |
| CheckScmInSrc                 | ANSIBLE0005 | Use scm key rather than src: scm+url in requirements file.        |                                                                      |
| CheckNamedTask                | ANSIBLE0006 | Tasks and handlers must be named.                                 | excludes: meta, debug, include\_\*, import\_\*, block                |
| CheckNameFormat               | ANSIBLE0007 | Name of tasks and handlers must be formatted.                     | formats: first letter capital                                        |
| CheckCommandInsteadofModule   | ANSIBLE0008 | Commands should not be used in place of modules.                  |                                                                      |
| CheckInstallUseLatest         | ANSIBLE0009 | Package managers should not install with state=latest.            |                                                                      |
| CheckShellInsteadCommand      | ANSIBLE0010 | Use Shell only when piping, redirecting or chaining commands.     |                                                                      |
| CheckCommandHasChanges        | ANSIBLE0011 | Commands should be idempotent and only used with some checks.     |                                                                      |
| CheckCompareToEmptyString     | ANSIBLE0012 | Don't compare to "" - use `when: var` or `when: not var`.         |                                                                      |
| CheckCompareToLiteralBool     | ANSIBLE0013 | Don't compare to True/False - use `when: var` or `when: not var`. |                                                                      |
| CheckLiteralBoolFormat        | ANSIBLE0014 | Literal bools should be written as `True/False` or `yes/no`.      | forbidden values are `true false TRUE FALSE Yes No YES NO`           |
| CheckBecomeUser               | ANSIBLE0015 | Become should be combined with become_user.                       |                                                                      |
| CheckFilterSeparation         | ANSIBLE0016 | Jinja2 filters should be separated with spaces.                   |                                                                      |
| CheckCommandInsteadOfArgument | ANSIBLE0017 | Commands should not be used in place of module arguments.         |                                                                      |
| CheckFilePermissionMissing    | ANSIBLE0018 | File permissions unset or incorrect.                              |                                                                      |
| CheckFilePermissionOctal      | ANSIBLE0019 | Octal file permissions must contain leading zero or be a string.  |                                                                      |
| CheckGitHasVersion            | ANSIBLE0020 | Git checkouts should use explicit version.                        |                                                                      |
| CheckMetaChangeFromDefault    | ANSIBLE0021 | Roles meta/main.yml default values should be changed.             |                                                                      |
| CheckWhenFormat               | ANSIBLE0022 | Don't use Jinja2 in `when`.                                       |                                                                      |
