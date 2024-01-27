import re

from ansiblelater.rule import RuleBase


class CheckFilterSeparation(RuleBase):
    rid = "ANS116"
    description = "Jinja2 filters should be separated with spaces"
    helptext = "no suitable numbers of spaces (required: 1)"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        matches = []
        braces = re.compile("{{(.*?)}}")
        filters = re.compile(r"(?<=\|)((\s{2,})*\S+)|(\S+(\s{2,})*)(?=\|)")

        if not errors:
            for i, line in yamllines:
                match = braces.findall(line)
                if match:
                    for item in match:
                        # replace potential regex in filters
                        item = re.sub(r"\(.+\)", "(dummy)", item)
                        matches.append((i, item))

            for i, item in matches:
                if filters.findall(item):
                    errors.append(self.Error(i, self.helptext))
        return self.Result(candidate.path, errors)
