---
title: Default settings
---

The default configuration is used if no other value is specified. Each option can be [overridden](/configuration/) in several ways.

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->
{{< highlight YAML "linenos=table" >}}
---
ansible:
  # Add the name of used custom Ansible modules. Otherwise ansible-later
  # can't detect unknown modules and will through an error.
  # Modules which are bundled with the role and placed in a './library'
  # directory will be auto-detected and don't need to be added to this list.
  custom_modules: []

  # Settings for variable formatting rule (ANSIBLE0004)
  double-braces:
    max-spaces-inside: 1
    min-spaces-inside: 1

  # List of allowed literal bools (ANSIBLE0014)
  literal-bools:
    - "True"
    - "False"
    - "yes"
    - "no"

# Global logging configuration
# If you would like to force colored output (e.g. non-tty)
# set environment variable `PY_COLORS=1`
logging:
  # You can enable JSON logging if a parsable output is required
  json: False

  # Possible options debug | info | warning | error | critical
  level: "warning"

# Global settings for all defined rules
rules:
  # Disable build-in rules if required
  buildin: True

  # List of files to exclude
  exclude_files: []
  # Examples:
  #  - molecule/
  #  - files/**/*.py

  # Limit checks to given rule ID's
  # If empty all rules will be used.
  filter: []

  # Exclude given rule ID's from checks
  exclude_filter: []

  # List of rule ID's that should be displayed as a warning instead of an error. By default,
  # only rules whose version is higher than the current default version are marked as warnings.
  # This list allows to degrade errors to warnings for each rule.
  warning_filter:
    - "ANSIBLE9999"

  # All dotfiles (including hidden folders) are excluded by default.
  # You can disable this setting and handle dotfiles by yourself with `exclude_files`.
  ignore_dotfiles: True

  # List of directories to load standard rules from (defaults to build-in)
  standards: []

  # Standard version to use. Standard version set in a roles meta file
  # or playbook will takes precedence.
  version:

# Block to control included yamllint rules.
# See https://yamllint.readthedocs.io/en/stable/rules.html
yamllint:
  colons:
    max-spaces-after: 1
    max-spaces-before: 0
  document-start:
    present: True
  empty-lines:
    max: 1
    max-end: 1
    max-start: 0
  hyphens:
    max-spaces-after: 1
  indentation:
    check-multi-line-strings: False
    indent-sequences: True
    spaces: 2
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
