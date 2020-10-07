---
title: Exclude tasks
---

If you want to ignore individual tasks completely, you can use the `skip_ansible_later` tag.

## Example

<!-- prettier-ignore-start -->
<!-- spellchecker-disable -->
<!-- markdownlint-disable -->
{{< highlight Yaml "linenos=table" >}}
- name: Excluded task
  command: "pwd"
  tags:
    - skip_ansible_later

{{< /highlight >}}
<!-- markdownlint-restore -->
<!-- spellchecker-enable -->
<!-- prettier-ignore-end -->
