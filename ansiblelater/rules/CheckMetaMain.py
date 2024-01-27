from nested_lookup import nested_lookup

from ansiblelater.rule import RuleBase


class CheckMetaMain(RuleBase):
    rid = "ANS102"
    description = "Roles must contain suitable meta/main.yml"
    helptext = "file should contain `{key}` key"
    types = ["meta"]

    def check(self, candidate, settings):
        content, errors = self.get_raw_yaml(candidate, settings)
        keys = ["author", "description", "min_ansible_version", "platforms"]

        if not errors:
            has_galaxy_info = isinstance(content, dict) and "galaxy_info" in content
            has_dependencies = isinstance(content, dict) and "dependencies" in content

            if not has_galaxy_info:
                errors.append(self.Error(None, self.helptext.format(key="galaxy_info")))

            if not has_dependencies:
                errors.append(self.Error(None, self.helptext.format(key="dependencies")))

            for key in keys:
                if has_galaxy_info and not nested_lookup(key, content.get("galaxy_info", {})):
                    errors.append(self.Error(None, self.helptext.format(key=key)))

        return self.Result(candidate.path, errors)
