from ansiblelater.rule import RuleBase


class CheckWhenFormat(RuleBase):
    rid = "ANS122"
    description = "Don't use Jinja2 in when"
    helptext = (
        "`when` is a raw Jinja2 expression, redundant `{{ }}` should be removed from variable(s)"
    )

    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)

        if not errors:
            for task in tasks:
                if "when" in task and not self._is_valid(task["when"]):
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)

    @staticmethod
    def _is_valid(when):
        if not isinstance(when, str):
            return True
        return when.find("{{") == -1 and when.find("}}") == -1
