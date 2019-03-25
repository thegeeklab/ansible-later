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

`ansible-later` does _**not**_ ensure that your role will work as expected.

The project name is an acronym for **L**ovely **A**utomation **TE**sting f**R**mework.

## Table of Content

- [ansible-later](#ansible-later)
  - [Table of Content](#table-of-content)
    - [Setup](#setup)
      - [Using pip](#using-pip)
      - [From source](#from-source)
    - [Usage](#usage)
      - [Configuration](#configuration)
      - [Review a git repositories](#review-a-git-repositories)
      - [Review a list of files](#review-a-list-of-files)
      - [Buildin rules](#buildin-rules)
    - [Build your own](#build-your-own)
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
git clone https://repourl
export PYTHONPATH=$PYTHONPATH:`pwd`/ansible-later/ansiblelater
export PATH=$PATH:`pwd`/ansible-later/ansiblelater/bin
```

### Usage

```Shell
ansible-later FILES
```

Where FILES is a space delimited list of files to review.
ansible-later is _not_ recursive and won't descend
into child folders; it just processes the list of files you give it.

Passing a folder in with the list of files will elicit a warning:

```Shell
WARN: Couldn't classify file ./foldername
```

ansible-later will review inventory files, role
files, python code (modules, plugins) and playbooks.

- The goal is that each file that changes in a
  changeset should be reviewable simply by passing
  those files as the arguments to ansible-later.
- Roles are slightly harder, and sub-roles are yet
  harder still (currently just using `-R` to process
  roles works very well, but doesn't examine the
  structure of the role)
- Using `{{ playbook_dir }}` in sub roles is so far
  very hard.
- This should work against various repository styles
  - per-role repository
  - roles with sub-roles
  - per-playbook repository
- It should work with roles requirement files and with local roles

#### Configuration

If your standards (and optionally inhouse rules) are set up, create
a configuration file in the appropriate location (this will depend on
your operating system)

The location can be found by using `ansible-later` with no arguments.

You can override the configuration file location with the `-c` flag.

```INI
[rules]
standards = /path/to/your/standards/rules
```

The standards directory can be overridden with the `-d` argument.

#### Review a git repositories

- `git ls-files | xargs ansible-later` works well in
  a roles repo to review the whole role. But it will
  review the whole of other repos too.
- `git ls-files *[^LICENSE,.md] | xargs ansible-later`
  works like the first example but excludes some
  unnecessary files.
- `git diff branch_to_compare | ansible-later` will
  review only the changes between the branches and
  surrounding context.

#### Review a list of files

- `find . -type f | xargs ansible-later` will review
  all files in the current folder (and all subfolders),
  even if they're not checked into git

#### Buildin rules

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

### Build your own

#### The standards file

A standards file comprises a list of standards, and optionally some methods to
check those standards.

Create a file called standards.py (this can import other modules)

```Python
from ansiblelater include Standard, Result

tasks_are_uniquely_named = Standard(dict(
    id="ANSIBLE0003",
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
| Inventory   | all files within the parent dir `inventory` and `inventory` or `hosts` in filename                                           |
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
