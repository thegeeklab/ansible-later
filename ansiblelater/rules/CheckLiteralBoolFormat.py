import re

from ansiblelater.standard import StandardBase


class CheckLiteralBoolFormat(StandardBase):

    sid = "ANSIBLE0014"
    description = "Literal bools should start with a capital letter"
    helptext = "literal bools should be written as `True/False` or `yes/no`"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        uppercase_bool = re.compile(r"([=!]=|:)\s*(true|false|TRUE|FALSE|Yes|No|YES|NO)\s*$")

        if not errors:
            for i, line in yamllines:
                if uppercase_bool.findall(line):
                    errors.append(self.Error(i, self.helptext))

        return self.Result(candidate.path, errors)
