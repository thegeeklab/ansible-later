import re
from collections import defaultdict

from ansiblelater.rule import RuleBase


class CheckTaskSeparation(RuleBase):
    rid = "ANS101"
    description = "Single tasks should be separated by empty line"
    helptext = "missing task separation (required: 1 empty line)"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        options = defaultdict(dict)
        options.update(remove_empty=False)
        options.update(remove_markers=False)

        yamllines, line_errors = self.get_normalized_yaml(candidate, settings, options)
        tasks, task_errors = self.get_normalized_tasks(candidate, settings)

        task_regex = re.compile(r"-\sname:(.*)")
        prevline = "#file_start_marker"

        allowed_prevline = [
            "---",
            "handlers:",
            "tasks:",
            "pre_tasks:",
            "post_tasks:",
            "block:",
            "rescue:",
            "always:",
        ]

        errors = task_errors + line_errors
        if not errors:
            for i, line in yamllines:
                match = task_regex.search(line)
                if match and prevline:
                    name = match.group(1).strip()

                    if not any(task.get("name") == name for task in tasks):
                        continue

                    if not any(item in prevline for item in allowed_prevline):
                        errors.append(self.Error(i, self.helptext))

                prevline = line.strip()

        return self.Result(candidate.path, errors)
