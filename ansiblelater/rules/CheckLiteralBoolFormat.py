import re

from ansiblelater.standard import StandardBase


class CheckLiteralBoolFormat(StandardBase):

    sid = "ANSIBLE0014"
    description = "Literal bools should be consistent"
    helptext = "literal bools should be written as `{bools}`"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        litera_bools = re.compile(r"(?:[=!]=|:)\s*(true|false|yes|no|on|off)\s*$", re.IGNORECASE)
        allowed = settings["ansible"]["literal-bools"]

        if not errors:
            for i, line in yamllines:
                matches = litera_bools.findall(line)
                if any(m not in allowed for m in matches):
                    errors.append(self.Error(i, self.helptext.format(bools=", ".join(allowed))))

        return self.Result(candidate.path, errors)
