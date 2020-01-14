---
title: Usage
---

```Shell
ansible-later FILES
```

If you don't pass any file to ansible-later it will review all files including subdirs in
the current working directory (hidden files and folders are excluded by default).

Otherwise you can pass a space delimited list of files to review. You can also pass glob
patterns to ansible-later:

{{< highlight Shell "linenos=table" >}}
# Review single files
ansible-later meta/main.yml tasks/install.yml

# Review all yml files (including subfolders)
ansible-later **/*.yml
{{< /highlight >}}

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
