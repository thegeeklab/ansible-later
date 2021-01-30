from ansiblelater.standard import StandardBase


class CheckYamlIndent(StandardBase):

    sid = "LINT0002"
    description = "YAML should not contain unnecessarily empty lines"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = "rules: {{document-start: {conf}}}".format(
            conf=settings["yamllint"]["document-start"]
        )
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
