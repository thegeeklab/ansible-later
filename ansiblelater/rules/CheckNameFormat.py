from collections import defaultdict

from ansiblelater.rule import RuleBase


class CheckNameFormat(RuleBase):
    rid = "ANS107"
    description = "Name of tasks and handlers must be formatted"
    helptext = "name `{name}` should start with uppercase"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        namelines = defaultdict(list)

        if not errors:
            for task in tasks:
                if "name" in task:
                    namelines[task["name"]].append(task["__line__"])
            for name, lines in namelines.items():
                if name and not name[0].isupper():
                    errors.append(self.Error(lines[-1], self.helptext.format(name=name)))

        return self.Result(candidate.path, errors)
