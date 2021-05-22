---
title: Candidated
---

Each file passed to `ansible-later` will be classified. The result is a `Candidate` object which contains some meta information and is an instance of one of following object types.

| Object type | Description                                                                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Task        | all files within the parent directory `tasks`                                                                                      |
| Handler     | all files within the parent directory `handler`                                                                                    |
| RoleVars    | all files within the parent directory `vars` or `default`                                                                          |
| GroupVars   | all files (including subdirectories) within the parent directory `group_vars`                                                      |
| HostVars    | all files (including subdirectories) within the parent directory `host_vars`                                                       |
| Meta        | all files within the parent directory `meta`                                                                                       |
| Code        | all files within the parent directory `library`, `lookup_plugins`, `callback_plugins` and `filter_plugins` or python files (`.py`) |
| Inventory   | all files within the parent directory `inventories` and `inventory` or `hosts` as filename                                         |
| Rolesfile   | all files with `rolesfile` or `requirements` in filename                                                                           |
| Makefile    | all files with `Makefile` in filename                                                                                              |
| Template    | all files (including subdirectories) within the parent directory `templates` or Jinja2 files (`.j2`)                               |
| File        | all files (including subdirectories) within the parent directory `files`                                                           |
| Playbook    | all YAML files (`.yml` or `.yaml`) not matching a previous object type                                                              |
| Doc         | all files with `README` in filename                                                                                                |
