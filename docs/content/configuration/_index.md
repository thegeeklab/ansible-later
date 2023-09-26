---
title: Configuration
---

ansible-later ships with some default settings that should be sufficient for most users to get started, but you can customize settings to suit your needs.

Changes can be made in a YAML configuration file or via CLI options, which are processed in the following order (last wins):

- default configuration (built-in)
- global configuration file (this depends on your operating system)
- folder-based configuration file (`.later.yml|.later.yaml|.later`) in the current working directory
- CLI options

Please note that YAML attributes are overwritten while YAML lists are merged in any configuration files.

To simplify the linting of individual files, e.g. for debugging purposes, ansible-later ignores the `exclude_files` and `ignore_dotfiles` options when files are passed to the CLI.
