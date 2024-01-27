from collections import defaultdict

from ansiblelater.rule import RuleBase


class CheckUniqueNamedTask(RuleBase):
    rid = "ANS103"
    description = "Tasks and handlers must be uniquely named within a single file"
    helptext = "name `{name}` appears multiple times"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)

        namelines = defaultdict(list)

        if not errors:
            for task in tasks:
                if "name" in task:
                    namelines[task["name"]].append(task["__line__"])
            for name, lines in namelines.items():
                if name and len(lines) > 1:
                    errors.append(self.Error(lines[-1], self.helptext.format(name=name)))

        return self.Result(candidate.path, errors)
