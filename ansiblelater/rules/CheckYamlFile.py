import os

from ansiblelater.rule import RuleBase


class CheckYamlFile(RuleBase):
    rid = "YML106"
    description = "Roles file should be in yaml format"
    helptext = "file does not have a .yml extension"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        errors = []
        extensions = [".yml", ".yaml"]

        if os.path.isfile(candidate.path) and os.path.splitext(candidate.path)[1] in extensions:
            content, errors = self.get_raw_yaml(candidate, settings)
        else:
            errors.append(self.Error(None, self.helptext))

        return self.Result(candidate.path, errors)
