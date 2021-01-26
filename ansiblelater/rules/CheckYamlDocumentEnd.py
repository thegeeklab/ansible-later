from ansiblelater.standard import StandardBase


class CheckYamlDocumentEnd(StandardBase):

    sid = "LINT0009"
    description = "YAML should contain document end marker"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        options = "rules: {{document-end: {conf}}}".format(
            conf=settings["yamllint"]["document-end"]
        )
        errors = self.run_yamllint(candidate, options)

        return self.Result(candidate.path, errors)
