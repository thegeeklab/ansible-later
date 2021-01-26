from ansiblelater.standard import StandardBase


class CheckCommandHasChanges(StandardBase):

    sid = "ANSIBLE0011"
    description = "Commands should be idempotent"
    helptext = (
        "commands should either read information (and thus set changed_when) or not "
        "do something if it has already been done (using creates/removes) "
        "or only do it if another check has a particular result (when)"
    )
    version = "0.1"
    types = ["playbook", "task"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        commands = ["command", "shell", "raw"]

        if not errors:
            for task in tasks:
                if task["action"]["__ansible_module__"] in commands:
                    if (
                        "changed_when" not in task and "when" not in task
                        and "when" not in task.get("__ansible_action_meta__", [])
                        and "creates" not in task["action"] and "removes" not in task["action"]
                    ):
                        errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
