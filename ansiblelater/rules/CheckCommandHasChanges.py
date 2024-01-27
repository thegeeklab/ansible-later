from ansiblelater.rule import RuleBase


class CheckCommandHasChanges(RuleBase):
    rid = "ANS111"
    description = "Commands should be idempotent"
    helptext = (
        "commands should only read while using `changed_when` or try to be "
        "idempotent while using controls like `creates`, `removes` or `when`"
    )
    types = ["playbook", "task"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        commands = ["command", "shell", "raw"]

        if not errors:
            for task in tasks:
                if task["action"]["__ansible_module__"] in commands and (
                    "changed_when" not in task
                    and "when" not in task
                    and "when" not in task.get("__ansible_action_meta__", [])
                    and "creates" not in task["action"]
                    and "removes" not in task["action"]
                ):
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
