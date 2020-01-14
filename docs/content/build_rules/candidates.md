---
title: Candidated
---

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
