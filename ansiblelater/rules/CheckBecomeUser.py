from ansiblelater.standard import StandardBase


class CheckBecomeUser(StandardBase):

    sid = "ANSIBLE0015"
    description = "Become should be combined with become_user"
    helptext = "the task has `become` enabled but `become_user` is missing"
    version = "0.1"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        true_value = [True, "true", "True", "TRUE", "yes", "Yes", "YES"]

        if not errors:
            gen = (task for task in tasks if "become" in task)
            for task in gen:
                if task["become"] in true_value and "become_user" not in task.keys():
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
