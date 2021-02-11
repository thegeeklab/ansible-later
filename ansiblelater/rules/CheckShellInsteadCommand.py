import re

from ansiblelater.standard import StandardBase


class CheckShellInsteadCommand(StandardBase):

    sid = "ANSIBLE0010"
    description = "Shell should only be used when essential"
    helptext = "shell should only be used when piping, redirecting or chaining commands"
    version = "0.1"
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

                    if "cmd" in task["action"]:
                        cmd = task["action"].get("cmd", [])
                    else:
                        cmd = " ".join(task["action"].get("__ansible_arguments__", []))

                    unjinja = re.sub(r"\{\{[^\}]*\}\}", "JINJA_VAR", cmd)
                    if not any(ch in unjinja for ch in "&|<>;$\n*[]{}?"):
                        errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
