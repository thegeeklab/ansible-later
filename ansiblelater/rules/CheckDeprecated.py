from ansiblelater.rule import RuleBase


class CheckDeprecated(RuleBase):
    rid = "ANS999"
    description = "Deprecated features should not be used"
    helptext = "`{old}` is deprecated and should not be used anymore. Use `{new}` instead."
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings, full=True)

        if not errors:
            for task in tasks:
                if "skip_ansible_lint" in (task.get("tags") or []):
                    errors.append(
                        self.Error(
                            task["__line__"],
                            self.helptext.format(
                                old="skip_ansible_lint", new="skip_ansible_later"
                            ),
                        )
                    )
        return self.Result(candidate.path, errors)
