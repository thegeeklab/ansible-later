---
title: The standards file
---

A standards file comprises a list of standards, and optionally some methods to
check those standards.

Create a file called standards.py (this can import other modules)

<!-- prettier-ignore-start -->
{{< highlight Python "linenos=table" >}}
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
{{< /highlight >}}
<!-- prettier-ignore-end -->

When you add new standards, you should increment the version of your standards. Your playbooks and roles should declare what version of standards you are using, otherwise ansible-later assumes you're using the latest. The declaration is done by adding standards version as first line in the file.

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
{{< highlight INI "linenos=table" >}}
# Standards: 1.2
{{< /highlight >}}
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

To add standards that are advisory, don't set the version. These will cause a message to be displayed but won't constitute a failure. When a standard version is higher than declared version, a message will be displayed 'WARN: Future standard' and won't constitute a failure.

An example standards file is available at [ansiblelater/examples/standards.py](ansiblelater/examples/standards.py)

If you only want to check one or two standards quickly (perhaps you want to review your entire code base for deprecated bare words), you can use the `-s` flag with the name of your standard. You can pass `-s` multiple times.

<!-- prettier-ignore-start -->
{{< highlight Shell "linenos=table" >}}
git ls-files | xargs ansible-later -s "bare words are deprecated for with_items"
{{< /highlight >}}
<!-- prettier-ignore-end -->

You can see the name of the standards being checked for each different file by running `ansible-later` with the `-v` option.
