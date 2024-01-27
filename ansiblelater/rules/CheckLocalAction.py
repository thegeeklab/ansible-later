# Copyright (c) 2016, Tsukinowa Inc. <info@tsukinowa.jp>
# Copyright (c) 2018, Ansible Project
from ansiblelater.rule import RuleBase


class CheckLocalAction(RuleBase):
    rid = "ANS124"
    description = "Don't use local_action"
    helptext = "`delegate_to: localhost` should be used instead of `local_action`"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        if not errors:
            for i, line in yamllines:
                if "local_action" in line:
                    errors.append(self.Error(i, self.helptext))

        return self.Result(candidate.path, errors)
