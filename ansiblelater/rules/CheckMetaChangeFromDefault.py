# Copyright (c) 2018, Ansible Project
from nested_lookup import nested_lookup

from ansiblelater.standard import StandardBase


class CheckMetaChangeFromDefault(StandardBase):

    sid = "ANSIBLE0021"
    description = "Roles meta/main.yml default values should be changed"
    helptext = "meta/main.yml default values should be changed for: `{field}`"
    version = "0.2"
    types = ["meta"]

    def check(self, candidate, settings):
        content, errors = self.get_raw_yaml(candidate, settings)
        field_defaults = [
            ("author", "your name"),
            ("description", "your description"),
            ("company", "your company (optional)"),
            ("license", "license (GPLv2, CC-BY, etc)"),
            ("license", "license (GPL-2.0-or-later, MIT, etc)"),
        ]

        if not errors:
            for field, default in field_defaults:
                pair = "{field}: {default}".format(field=field, default=default)
                lookup = nested_lookup(field, content)
                if lookup and default in nested_lookup(field, content):
                    errors.append(self.Error(None, self.helptext.format(field=pair)))

        return self.Result(candidate.path, errors)
