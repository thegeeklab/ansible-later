from ansiblelater.standard import StandardBase


class CheckYamlDocumentStart(StandardBase):

    sid = "LINT0004"
    description = "YAML should contain document start marker"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = "rules: {{document-start: {conf}}}".format(
            conf=settings["yamllint"]["document-start"]
        )
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
