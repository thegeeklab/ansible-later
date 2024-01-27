from ansiblelater.rule import RuleBase


class CheckYamlColons(RuleBase):
    rid = "YML105"
    description = "YAML should use consistent number of spaces around colons"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{colons: {settings['yamllint']['colons']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
