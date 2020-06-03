---
title: CLI options
---

You can get all available CLI options by running `ansible-later --help`:

<!-- prettier-ignore-start -->
{{< highlight Shell "linenos=table" >}}
$ ansible-later --help
usage: ansible-later [-h] [-c CONFIG_FILE] [-r RULES.STANDARDS]
                     [-s RULES.FILTER] [-v] [-q] [--version]
                     [rules.files [rules.files ...]]

Validate Ansible files against best practice guideline

positional arguments:
  rules.files

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        location of configuration file
  -r RULES.STANDARDS, --rules RULES.STANDARDS
                        location of standards rules
  -s RULES.FILTER, --standards RULES.FILTER
                        limit standards to given ID's
  -x RULES.EXCLUDE_FILTER, --exclude-standards RULES.EXCLUDE_FILTER
                        exclude standards by given ID's
  -v                    increase log level
  -q                    decrease log level
  --version             show program's version number and exit
{{< /highlight >}}
<!-- prettier-ignore-end -->
