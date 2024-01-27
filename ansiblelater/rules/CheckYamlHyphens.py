from ansiblelater.rule import RuleBase


class CheckYamlHyphens(RuleBase):
    rid = "YML103"
    description = "YAML should use consistent number of spaces after hyphens"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{hyphens: {settings['yamllint']['hyphens']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
