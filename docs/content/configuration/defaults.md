---
title: Default settings
---

{{< highlight YAML "linenos=table" >}}
---
ansible:
  # Add the name of used custom ansible modules.
  # Otherwise ansible-later can't detect unknown modules
  # and will through an error.
  custom_modules: []
  # Settings for variable formatting rule (ANSIBLE0004)
  double-braces:
    max-spaces-inside: 1
    min-spaces-inside: 1

# Global logging configuration
# If you would like to force colored output (e.g. non-tty)
# set emvironment variable `PY_COLORS=1`
logging:
  # You can enable json logging if a parsable output is required
  json: False
  # Possible options debug | info | warning | error | critical
  level: "warning"

# Global settings for all defined rules
rules:
  # list of files to exclude
  exclude_files: []
  # Examples:
  #  - molecule/
  #  - files/**/*.py

  # Limit checks to given rule ID's
  # If empty all rules will be used.
  filter: []

  # Exclude given rule ID's from checks
  exclude_filter: []
  
  # All dotfiles (including hidden folders) are excluded by default.
  # You can disable this setting and handle dotfiles by yourself with `exclude_files`.
  ignore_dotfiles: True
  # Path to the folder containing your custom standards file
  standards: ansiblelater/data

# Block to control included yamlllint rules.
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
