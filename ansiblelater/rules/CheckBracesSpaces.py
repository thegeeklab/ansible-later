import re

from ansiblelater.standard import StandardBase
from ansiblelater.utils import count_spaces


class CheckBracesSpaces(StandardBase):

    sid = "ANSIBLE0004"
    description = "YAML should use consistent number of spaces around variables"
    helptext = "no suitable numbers of spaces (min: {min} max: {max})"
    version = "0.1"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars", "meta"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)
        conf = settings["ansible"]["double-braces"]

        matches = []
        braces = re.compile("{{(.*?)}}")

        if not errors:
            for i, line in yamllines:
                if "!unsafe" in line:
                    continue
                match = braces.findall(line)
                if match:
                    for item in match:
                        matches.append((i, item))

            for i, line in matches:
                [leading, trailing] = count_spaces(line)
                sum_spaces = leading + trailing

                if (
                    sum_spaces < conf["min-spaces-inside"] * 2
                    or sum_spaces > conf["min-spaces-inside"] * 2
                ):
                    errors.append(
                        self.Error(
                            i,
                            self.helptext.format(
                                min=conf["min-spaces-inside"], max=conf["max-spaces-inside"]
                            )
                        )
                    )
        return self.Result(candidate.path, errors)
