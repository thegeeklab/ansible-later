from ansiblelater.rule import RuleBase


class CheckYamlDocumentStart(RuleBase):
    sid = "LINT0004"
    description = "YAML should contain document start marker"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{document-start: {settings['yamllint']['document-start']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
