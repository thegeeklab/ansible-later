import re

from ansiblelater.candidate import Template
from ansiblelater.standard import StandardBase


class CheckCompareToEmptyString(StandardBase):

    sid = "ANSIBLE0012"
    description = "Don't compare to empty string \"\""
    helptext = ("use `when: var` rather than `when: var !=` (or conversely `when: not var`)")
    version = "0.1"
    types = ["playbook", "task", "handler", "template"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)

        if not errors:
            if isinstance(candidate, Template):
                matches = []
                jinja_string = re.compile("({{|{%)(.*?)(}}|%})")

                for i, line in yamllines:
                    match = jinja_string.findall(line)
                    if match:
                        for item in match:
                            matches.append((i, item[1]))

                yamllines = matches

            empty_string_compare = re.compile("[=!]= ?[\"'][\"']")

            for i, line in yamllines:
                if empty_string_compare.findall(line):
                    errors.append(self.Error(i, self.helptext))

        return self.Result(candidate.path, errors)
