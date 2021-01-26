from nested_lookup import nested_lookup

from ansiblelater.standard import StandardBase


class CheckMetaMain(StandardBase):

    sid = "ANSIBLE0002"
    description = "Roles must contain suitable meta/main.yml"
    helptext = "file should contain '{key}' key"
    version = "0.1"
    types = ["meta"]

    def check(self, candidate, settings):
        content, errors = self.get_raw_yaml(candidate, settings)
        keys = ["author", "description", "min_ansible_version", "platforms", "dependencies"]

        if not errors:
            for key in keys:
                if not nested_lookup(key, content):
                    errors.append(self.Error(None, self.helptext.format(key=key)))

        return self.Result(candidate.path, errors)
