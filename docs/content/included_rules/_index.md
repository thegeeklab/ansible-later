---
title: Included rules
---

Reviews are useless without some rules to check against. `ansible-later` comes with a set of built-in checks, which are explained in the following table.

| Rule                          | ID     | Description                                                       | Parameter                                                                  |
| ----------------------------- | ------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------- |
| CheckYamlEmptyLines           | YML101 | YAML should not contain unnecessarily empty lines.                | {max: 1, max-start: 0, max-end: 1}                                         |
| CheckYamlIndent               | YML102 | YAML should be correctly indented.                                | {spaces: 2, check-multi-line-strings: false, indent-sequences: true}       |
| CheckYamlHyphens              | YML103 | YAML should use consistent number of spaces after hyphens (-).    | {max-spaces-after: 1}                                                      |
| CheckYamlDocumentStart        | YML104 | YAML should contain document start marker.                        | {document-start: {present: true}}                                          |
| CheckYamlColons               | YML105 | YAML should use consistent number of spaces around colons.        | {colons: {max-spaces-before: 0, max-spaces-after: 1}}                      |
| CheckYamlFile                 | YML106 | Roles file should be in YAML format.                              |                                                                            |
| CheckYamlHasContent           | YML107 | Files should contain useful content.                              |                                                                            |
| CheckNativeYaml               | YML108 | Use YAML format for tasks and handlers rather than key=value.     | {native-yaml: {exclude: []}}                                               |
| CheckYamlDocumentEnd          | YML109 | YAML should contain document end marker.                          | {document-end: {present: true}}                                            |
| CheckYamlOctalValues          | YML110 | YAML should not use forbidden implicit or explicit octal value.   | {octal-values: {forbid-implicit-octal: true, forbid-explicit-octal: true}} |
| CheckTaskSeparation           | ANS101 | Single tasks should be separated by an empty line.                |                                                                            |
| CheckMetaMain                 | ANS102 | Meta file should contain a basic subset of parameters.            | author, description, min_ansible_version, platforms, dependencies          |
| CheckUniqueNamedTask          | ANS103 | Tasks and handlers must be uniquely named within a file.          |                                                                            |
| CheckBraces                   | ANS104 | YAML should use consistent number of spaces around variables.     | {double-braces: max-spaces-inside: 1, min-spaces-inside: 1}                |
| CheckScmInSrc                 | ANS105 | Use SCM key rather than `src: scm+url` in requirements file.      |                                                                            |
| CheckNamedTask                | ANS106 | Tasks and handlers must be named.                                 | {named-task: {exclude: [meta, debug, block, include\_\*, import\_\*]}}     |
| CheckNameFormat               | ANS107 | Name of tasks and handlers must be formatted.                     | formats: first letter capital                                              |
| CheckCommandInsteadofModule   | ANS108 | Commands should not be used in place of modules.                  |                                                                            |
| CheckInstallUseLatest         | ANS109 | Package managers should not install with state=latest.            |                                                                            |
| CheckShellInsteadCommand      | ANS110 | Use Shell only when piping, redirecting or chaining commands.     |                                                                            |
| CheckCommandHasChanges        | ANS111 | Commands should be idempotent and only used with some checks.     |                                                                            |
| CheckCompareToEmptyString     | ANS112 | Don't compare to "" - use `when: var` or `when: not var`.         |                                                                            |
| CheckCompareToLiteralBool     | ANS113 | Don't compare to True/False - use `when: var` or `when: not var`. |                                                                            |
| CheckLiteralBoolFormat        | ANS114 | Literal bools should be consistent.                               | {literal-bools: [True, False, yes, no]}                                    |
| CheckBecomeUser               | ANS115 | Become should be combined with become_user.                       |                                                                            |
| CheckFilterSeparation         | ANS116 | Jinja2 filters should be separated with spaces.                   |                                                                            |
| CheckCommandInsteadOfArgument | ANS117 | Commands should not be used in place of module arguments.         |                                                                            |
| CheckFilePermissionMissing    | ANS118 | File permissions unset or incorrect.                              |                                                                            |
| CheckFilePermissionOctal      | ANS119 | Octal file permissions must contain leading zero or be a string.  |                                                                            |
| CheckGitHasVersion            | ANS120 | Git checkouts should use explicit version.                        |                                                                            |
| CheckMetaChangeFromDefault    | ANS121 | Roles meta/main.yml default values should be changed.             |                                                                            |
| CheckWhenFormat               | ANS122 | Don't use Jinja2 in `when`.                                       |                                                                            |
| CheckNestedJinja              | ANS123 | Don't use nested Jinja2 pattern.                                  |                                                                            |
| CheckLocalAction              | ANS124 | Don't use local_action.                                           |                                                                            |
| CheckRelativeRolePaths        | ANS125 | Don't use a relative path in a role.                              |                                                                            |
| CheckChangedInWhen            | ANS126 | Use handlers instead of `when: changed`.                          |                                                                            |
| CheckChangedInWhen            | ANS127 | Deprecated bare variables in loops must not be used.              |                                                                            |
| CheckFQCNBuiltin              | ANS128 | Module actions should use full qualified collection names.        |                                                                            |
| CheckDeprecated               | ANS999 | Deprecated features of `ansible-later` should not be used.        |                                                                            |
