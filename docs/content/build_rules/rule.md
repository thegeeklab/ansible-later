---
title: Write a rule
---

A typical rule check will look like:

<!-- prettier-ignore-start -->
<!-- spellchecker-disable -->
{{< highlight Python "linenos=table" >}}
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
                if task["become"] in true_value and "become_user" not in task.keys():
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- prettier-ignore-end -->

They return a `Result` object, which contains a possibly empty list of `Error` objects. `Error` objects are formed of a line number and a message. If the error applies to the whole file being reviewed, set the line number to `None`.
