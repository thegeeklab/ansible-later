from ansiblelater.rule import RuleBase


class CheckBecomeUser(RuleBase):
    rid = "ANS115"
    description = "Become should be combined with become_user"
    helptext = "the task has `become` enabled but `become_user` is missing"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        true_value = [True, "true", "True", "TRUE", "yes", "Yes", "YES"]

        if not errors:
            gen = (task for task in tasks if "become" in task)
            for task in gen:
                if task["become"] in true_value and "become_user" not in task:
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
