---
title: Configuration
---

ansible-later comes with some default settigs which should be sufficent for most users to start,
but you can adjust most settings to your needs.

Changes can be made in a yaml configuration file or through cli options
which will be processed in the following order (last wins):

- default config (build-in)
- global config file (this will depend on your operating system)
- folderbased config file (`.later.yml` file in current working folder)
- cli options

Be careful! YAML Attributes will be overwritten while lists in any
config file will be merged.

To make it easier to review a singel file e.g. for debugging purpose, amsible-later
will ignore `exclude_files` and `ignore_dotfiles` options.
