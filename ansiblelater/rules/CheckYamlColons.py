from ansiblelater.standard import StandardBase


class CheckYamlColons(StandardBase):

    sid = "LINT0005"
    description = "YAML should use consistent number of spaces around colons"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = "rules: {{colons: {conf}}}".format(conf=settings["yamllint"]["colons"])
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
