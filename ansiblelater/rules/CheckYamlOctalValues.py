from ansiblelater.rule import RuleBase


class CheckYamlOctalValues(RuleBase):
    rid = "YML110"
    description = "YAML implicit/explicit octal value should match configuration"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{octal-values: {settings['yamllint']['octal-values']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
