from ansiblelater.standard import StandardBase


class CheckYamlEmptyLines(StandardBase):
    sid = "LINT0001"
    description = "YAML should not contain unnecessarily empty lines"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{empty-lines: {settings['yamllint']['empty-lines']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
