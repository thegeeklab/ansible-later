import re

from ansiblelater.standard import StandardBase


class CheckFilterSeparation(StandardBase):

    sid = "ANSIBLE0016"
    description = "Jinja2 filters should be separated with spaces"
    helptext = "no suitable numbers of spaces (required: 1)"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        matches = []
        braces = re.compile("{{(.*?)}}")
        filters = re.compile(r"(?<=\|)([\s]{2,}[^\s}]+|[^\s]+)|([^\s{]+[\s]{2,}|[^\s]+)(?=\|)")

        if not errors:
            for i, line in yamllines:
                match = braces.findall(line)
                if match:
                    for item in match:
                        matches.append((i, item))

            for i, line in matches:
                if filters.findall(line):
                    errors.append(self.Error(i, self.helptext))
        return self.Result(candidate.path, errors)
