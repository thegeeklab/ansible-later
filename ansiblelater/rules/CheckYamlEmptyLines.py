from ansiblelater.rule import RuleBase


class CheckYamlEmptyLines(RuleBase):
    rid = "YML101"
    description = "YAML should not contain unnecessarily empty lines"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{empty-lines: {settings['yamllint']['empty-lines']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
