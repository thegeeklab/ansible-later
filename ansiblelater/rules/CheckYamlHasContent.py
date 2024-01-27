from ansiblelater.rule import RuleBase


class CheckYamlHasContent(RuleBase):
    rid = "YML107"
    description = "Files should contain useful content"
    helptext = "the file appears to have no useful content"
    types = ["playbook", "task", "handler", "rolevars", "defaults", "meta"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        if (not candidate.faulty and len(yamllines) == 0) and not errors:
            errors.append(self.Error(None, self.helptext))

        return self.Result(candidate.path, errors)
