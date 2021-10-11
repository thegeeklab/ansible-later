---
title: Using pip
---

ansible-later requires a working Ansible installation. If Ansible is not already installed on your system you can to install `ansible-later` with one of the optional dependency groups `ansible` or `ansible-core`.

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->
{{< highlight Shell "linenos=table" >}}
# From pip as user
pip install ansible-later[ansible] --user  # or ansible-later[ansible-core]

# .. or as root
sudo pip install ansible-later[ansible]  # or ansible-later[ansible-core]
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
