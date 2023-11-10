from ansiblelater.standard import StandardBase


class CheckVersion(StandardBase):
    sid = "ANSIBLE9998"
    description = "Standards version should be pinned"
    helptext = "Standards version not set. Using latest standards version {version}"
    types = ["task", "handler", "rolevars", "meta", "template", "file", "playbook"]

    def check(self, candidate, settings):  # noqa
        errors = []

        if not candidate.version_config:
            errors.append(self.Error(None, self.helptext.format(version=candidate.version)))

        return self.Result(candidate.path, errors)
