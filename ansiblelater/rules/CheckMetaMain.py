from nested_lookup import nested_lookup

from ansiblelater.standard import StandardBase


class CheckMetaMain(StandardBase):

    sid = "ANSIBLE0002"
    description = "Roles must contain suitable meta/main.yml"
    helptext = "file should contain `{key}` key"
    version = "0.1"
    types = ["meta"]

    def check(self, candidate, settings):
        content, errors = self.get_raw_yaml(candidate, settings)
        keys = ["author", "description", "min_ansible_version", "platforms"]

        if not errors:
            has_galaxy_info = (isinstance(content, dict) and "galaxy_info" in content.keys())
            has_dependencies = (isinstance(content, dict) and "dependencies" in content.keys())

            if not has_galaxy_info:
                errors.append(self.Error(None, self.helptext.format(key="galaxy_info")))

            if not has_dependencies:
                errors.append(self.Error(None, self.helptext.format(key="dependencies")))

            for key in keys:
                if has_galaxy_info and not nested_lookup(key, content.get("galaxy_info", {})):
                    errors.append(self.Error(None, self.helptext.format(key=key)))

        return self.Result(candidate.path, errors)
