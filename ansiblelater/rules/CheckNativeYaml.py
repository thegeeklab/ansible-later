from ansiblelater.standard import StandardBase


class CheckNativeYaml(StandardBase):

    sid = "LINT0008"
    description = "Use YAML format for tasks and handlers rather than key=value"
    helptext = "task arguments appear to be in key value rather than YAML format"
    version = "0.1"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_action_tasks(candidate, settings)

        if not errors:
            for task in tasks:
                normal_form, error = self.get_normalized_task(task, candidate, settings)
                if error:
                    errors.extend(error)
                    break

                action = normal_form["action"]["__ansible_module__"]
                arguments = [
                    bytes(x, "utf-8").decode("utf8", "ignore")
                    for x in normal_form["action"]["__ansible_arguments__"]
                ]
                # Cope with `set_fact` where task["set_fact"] is None
                if not task.get(action):
                    continue
                if isinstance(task[action], dict):
                    continue
                # strip additional newlines off task[action]
                task_action = bytes(task[action].strip(), "utf-8").decode("utf8", "ignore")
                if list(filter(lambda a: a != "\\", task_action.split())) != arguments:
                    errors.append(self.Error(task["__line__"], self.helptext))
        return self.Result(candidate.path, errors)
