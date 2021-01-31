# Copyright (c) 2016, Tsukinowa Inc. <info@tsukinowa.jp>
# Copyright (c) 2018, Ansible Project
from ansiblelater.standard import StandardBase


class CheckLocalAction(StandardBase):

    sid = "ANSIBLE0024"
    description = "Don't use local_action"
    helptext = ("`delegate_to: localhost` should be used instead of `local_action`")
    version = "0.2"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        if not errors:
            for i, line in yamllines:
                if "local_action" in line:
                    errors.append(self.Error(i, self.helptext))

        return self.Result(candidate.path, errors)
