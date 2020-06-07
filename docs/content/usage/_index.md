---
title: Usage
---

```Shell
ansible-later FILES
```

If you don't pass any file to ansible-later it will review all files including sub-directories in the current working directory (hidden files and folders are excluded by default). Otherwise you can pass a space delimited list of files to review. You can also pass glob patterns to ansible-later:

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->
{{< highlight Shell "linenos=table" >}}
# Review single files
ansible-later meta/main.yml tasks/install.yml

# Review all yml files (including sub-directories)
ansible-later **/*.yml
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

ansible-later will review inventory files, role files, python code (modules, plugins) and playbooks. The goal is that each file that changes in a changeset should be reviewable simply by passing those files as the arguments to ansible-later.
