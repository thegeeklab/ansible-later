---
title: CLI options
---

You can get all available CLI options by running `ansible-later --help`:

<!-- prettier-ignore-start -->
<!-- spellchecker-disable -->
{{< highlight Shell "linenos=table" >}}
$ ansible-later --help
usage: ansible-later [-h] [-c CONFIG] [-r DIR] [-B] [-i TAGS] [-x TAGS] [-v] [-q] [-V] [rules.files ...]

Validate Ansible files against best practice guideline

positional arguments:
  rules.files

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to configuration file
  -r DIR, --rules-dir DIR
                        directory of rules
  -B, --no-builtin      disables built-in rules
  -i TAGS, --include-rules TAGS
                        limit rules to given id/tags
  -x TAGS, --exclude-rules TAGS
                        exclude rules by given it/tags
  -v                    increase log level
  -q                    decrease log level
  -V, --version         show program's version number and exit
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- prettier-ignore-end -->
