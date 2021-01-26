from ansiblelater.standard import StandardBase


class CheckNamedTask(StandardBase):

    sid = "ANSIBLE0006"
    description = "Tasks and handlers must be named"
    helptext = "module '{module}' used without or empty `name` attribute"
    version = "0.1"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        nameless_tasks = [
            "meta", "debug", "include_role", "import_role", "include_tasks", "import_tasks",
            "include_vars", "block"
        ]

        if not errors:
            for task in tasks:
                module = task["action"]["__ansible_module__"]
                if ("name" not in task or not task["name"]) and module not in nameless_tasks:
                    errors.append(
                        self.Error(task["__line__"], self.helptext.format(module=module))
                    )

        return self.Result(candidate.path, errors)
