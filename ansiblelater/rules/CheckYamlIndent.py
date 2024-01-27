from ansiblelater.rule import RuleBase


class CheckYamlIndent(RuleBase):
    rid = "YML102"
    description = "YAML should not contain unnecessarily empty lines"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{document-start: {settings['yamllint']['document-start']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
