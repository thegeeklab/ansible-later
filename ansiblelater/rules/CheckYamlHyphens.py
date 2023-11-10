from ansiblelater.standard import StandardBase


class CheckYamlHyphens(StandardBase):
    sid = "LINT0003"
    description = "YAML should use consistent number of spaces after hyphens"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = f"rules: {{hyphens: {settings['yamllint']['hyphens']}}}"
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
