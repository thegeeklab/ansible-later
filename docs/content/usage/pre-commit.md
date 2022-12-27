---
title: Pre-Commit
---

ansible-later can be used with the [pre-commit][pre-commit] framework:

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->
{{< highlight yaml "linenos=table" >}}
- repo: https://github.com/thegeeklab/ansible-later
  rev: v3.0.2  # or whatever tag you want
  hooks:
    - id: ansible-later
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

[pre-commit]: https://pre-commit.com/
