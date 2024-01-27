from ansiblelater.rule import RuleBase


class CheckShellInsteadCommand(RuleBase):
    rid = "ANS110"
    description = "Shell should only be used when essential"
    helptext = "shell should only be used when piping, redirecting or chaining commands"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)

        if not errors:
            for task in tasks:
                if task["action"]["__ansible_module__"] == "shell":
                    # skip processing if args.executable is used as this
                    # parameter is no longer support by command module
                    if "executable" in task["action"]:
                        continue

                    cmd = self.get_safe_cmd(task)
                    if not any(ch in cmd for ch in self.SHELL_PIPE_CHARS):
                        errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
