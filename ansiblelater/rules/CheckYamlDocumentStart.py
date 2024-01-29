from ansiblelater.rule import RuleBase


class CheckYamlDocumentStart(RuleBase):
    rid = "YML104"
    description = "YAML document start marker should match configuration"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{document-start: {settings['yamllint']['document-start']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
