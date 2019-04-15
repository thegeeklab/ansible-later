# ansible-later

[![Build Status](https://cloud.drone.io/api/badges/xoxys/ansible-later/status.svg)](https://cloud.drone.io/xoxys/ansible-later)
[![](https://img.shields.io/pypi/pyversions/ansible-later.svg)](https://pypi.org/project/ansible-later/)
[![](https://img.shields.io/pypi/status/ansible-later.svg)](https://pypi.org/project/ansible-later/)
[![](https://img.shields.io/pypi/v/ansible-later.svg)](https://pypi.org/project/ansible-later/)
[![codecov](https://codecov.io/gh/xoxys/ansible-later/branch/master/graph/badge.svg)](https://codecov.io/gh/xoxys/ansible-later)

This is a fork of Will Thames [ansible-review](https://github.com/willthames/ansible-review) so credits goes to him
for his work on ansible-review and ansible-lint.

`ansible-later` is a best pratice scanner and linting tool. In most cases, if you write ansibel roles in a team,
it helps to have a coding or best practice guideline in place. This will make ansible roles more readable for all
maintainers and can reduce the troubleshooting time.

`ansible-later` does _**not**_ ensure that your role will work as expected. For Deployment test you can use other tools
like [molecule](https://github.com/ansible/molecule).

The project name is an acronym for **L**ovely **A**utomation **TE**sting f**R**mework.

## Table of Content

- [Setup](#setup)
  - [Using pip](#using-pip)
  - [From source](#from-source)
- [Configuration](#configuration)
  - [Default settings](#default-settings)
  - [CLI Options](#cli-options)
- [Usage](#usage)
- [Buildin rules](#buildin-rules)
- [Build your own rules](#build-your-own-rules)
  - [The standards file](#the-standards-file)
  - [Candidates](#candidates)
  - [Minimal standards checks](#minimal-standards-checks)
- [License](#license)
- [Maintainers and Contributors](#maintainers-and-contributors)

---

### Setup

#### Using pip

```Shell
# From internal pip repo as user
pip install ansible-later --user

# .. or as root
sudo pip install ansible-later
```

#### From source

```Shell
# Install dependency
git clone https://github.com/xoxys/ansible-later
export PYTHONPATH=$PYTHONPATH:`pwd`/ansible-later/ansiblelater
export PATH=$PATH:`pwd`/ansible-later/bin
```

### Configuration

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

#### Default settings

```YAML
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

  # List of Ansible rule ID's
  # If empty all rules will be used.
  filter: []
  
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
```

#### CLI Options

You can get all available cli options by running `ansible-later --help`:

```Shell
$ ansible-later --help
usage: ansible-later [-h] [-c CONFIG_FILE] [-r RULES.STANDARDS]
                     [-s RULES.FILTER] [-v] [-q] [--version]
                     [rules.files [rules.files ...]]

Validate ansible files against best pratice guideline

positional arguments:
  rules.files

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        location of configuration file
  -r RULES.STANDARDS, --rules RULES.STANDARDS
                        location of standards rules
  -s RULES.FILTER, --standards RULES.FILTER
                        limit standards to specific ID's
  -v                    increase log level
  -q                    decrease log level
  --version             show program's version number and exit
```

### Usage

```Shell
ansible-later FILES
```

If you don't pass any file to ansible-later it will review all files including subdirs in
the current working directory (hidden files and folders are excluded by default).

Otherwise you can pass a space delimited list of files to review. You can also pass glob
patterns to ansible-later:

```Shell
# Review single files
ansible-later meta/main.yml tasks/install.yml

# Review all yml files (including subfolders)
ansible-later **/*.yml
```

ansible-later will review inventory files, role files, python code (modules, plugins)
and playbooks.

- The goal is that each file that changes in a
  changeset should be reviewable simply by passing
  those files as the arguments to ansible-later.
- Using `{{ playbook_dir }}` in sub roles is so far
  very hard.
- This should work against various repository styles
  - per-role repository
  - roles with sub-roles
  - per-playbook repository
- It should work with roles requirement files and with local roles

### Buildin rules

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

### Build your own rules

#### The standards file

A standards file comprises a list of standards, and optionally some methods to
check those standards.

Create a file called standards.py (this can import other modules)

```Python
from ansiblelater include Standard, Result

tasks_are_uniquely_named = Standard(dict(
    # ID's are optional but if you use ID's they have to be unique
    id="ANSIBLE0003",
    # Short description of the standard goal
    name="Tasks and handlers must be uniquely named within a single file",
    check=check_unique_named_task,
    version="0.1",
    types=["playbook", "task", "handler"],
))

standards = [
  tasks_are_uniquely_named,
  role_must_contain_meta_main,
]
```

When you add new standards, you should increment the version of your standards.
Your playbooks and roles should declare what version of standards you are
using, otherwise ansible-later assumes you're using the latest. The declaration
is done by adding standards version as first line in the file. e.g.

```INI
# Standards: 1.2
```

To add standards that are advisory, don't set the version. These will cause
a message to be displayed but won't constitute a failure.

When a standard version is higher than declared version, a message will be
displayed 'WARN: Future standard' and won't constitute a failure.

An example standards file is available at
[ansiblelater/examples/standards.py](ansiblelater/examples/standards.py)

If you only want to check one or two standards quickly (perhaps you want
to review your entire code base for deprecated bare words), you can use the
`-s` flag with the name of your standard. You can pass `-s` multiple times.

```Shell
git ls-files | xargs ansible-later -s "bare words are deprecated for with_items"
```

You can see the name of the standards being checked for each different file by running
`ansible-later` with the `-v` option.

#### Candidates

Each file passed to `ansible-later` will be classified. The result is a `Candidate` object
which contains some meta informations and is an instance of one of following object types.

| Object type | Description                                                                                                                  |
|-------------|------------------------------------------------------------------------------------------------------------------------------|
| Task        | all files within the parent dir `tasks`                                                                                      |
| Handler     | all files within the parent dir `handler`                                                                                    |
| RoleVars    | all files within the parent dir `vars` or `default`                                                                          |
| GroupVars   | all files (including subdirs) within the parent dir `group_vars`                                                             |
| HostVars    | all files (including subdirs) within the parent dir `host_vars`                                                              |
| Meta        | all files within the parent dir `meta`                                                                                       |
| Code        | all files within the parent dir `library`, `lookup_plugins`, `callback_plugins` and `filter_plugins` or python files (`.py`) |
| Inventory   | all files within the parent dir `inventories` and `inventory` or `hosts` as filename                                         |
| Rolesfile   | all files with `rolesfile` or `requirements` in filename                                                                     |
| Makefile    | all files with `Makefile` in filename                                                                                        |
| Template    | all files (including subdirs) within the parent dir `templates` or jinja2 files (`.j2`)                                      |
| File        | all files (including subdirs) within the parent dir `files`                                                                  |
| Playbook    | all yaml files (`.yml` or `.yaml`) not maching a previous object type                                                        |
| Doc         | all files with `README` in filename                                                                                          |

#### Minimal standards checks

A typical standards check will look like:

```Python
def check_playbook_for_something(candidate, settings):
    result = Result(candidate.path) # empty result is a success with no output
    with open(candidate.path, 'r') as f:
        for (lineno, line) in enumerate(f):
            if line is dodgy:
                # enumerate is 0-based so add 1 to lineno
                result.errors.append(Error(lineno+1, "Line is dodgy: reasons"))
    return result
```

All standards check take a candidate object, which has a path attribute.
The type can be inferred from the class name (i.e. `type(candidate).__name__`)
or from the table [here](#candidates).

They return a `Result` object, which contains a possibly empty list of `Error`
objects. `Error` objects are formed of a line number and a message. If the
error applies to the whole file being reviewed, set the line number to `None`.
Line numbers are important as `ansible-later` can review just ranges of files
to only review changes (e.g. through piping the output of `git diff` to
`ansible-later`).

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Maintainers and Contributors

[Robert Kaussow](https://github.com/xoxys)
