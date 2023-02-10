---
title: Pre-Commit setup
---

To use `ansible-later` with the [pre-commit](https://pre-commit.com/) framework, add the following to the `.pre-commit-config.yaml` file in your local repository.

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->

{{< highlight yaml "linenos=table" >}}
- repo: https://github.com/thegeeklab/ansible-later
  # change ref to the latest release from https://github.com/thegeeklab/ansible-later/releases
  rev: v3.0.2
  hooks:
    - id: ansible-later
{{< /highlight >}}

<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
