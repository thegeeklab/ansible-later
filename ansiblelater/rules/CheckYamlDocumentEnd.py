from ansiblelater.rule import RuleBase


class CheckYamlDocumentEnd(RuleBase):
    rid = "YML109"
    description = "YAML document end marker should match configuration"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{document-end: {settings['yamllint']['document-end']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
