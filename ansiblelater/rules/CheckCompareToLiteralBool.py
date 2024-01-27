import re

from ansiblelater.candidate import Template
from ansiblelater.rule import RuleBase


class CheckCompareToLiteralBool(RuleBase):
    rid = "ANS113"
    description = "Don't compare to True or False"
    helptext = "use `when: var` rather than `when: var == True` (or conversely `when: not var`)"
    types = ["playbook", "task", "handler"]

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

            literal_bool_compare = re.compile("[=!]= ?(True|true|False|false)")

            for i, line in yamllines:
                if literal_bool_compare.findall(line):
                    errors.append(self.Error(i, self.helptext))

        return self.Result(candidate.path, errors)
