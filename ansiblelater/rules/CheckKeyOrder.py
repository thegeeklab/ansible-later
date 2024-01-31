# Original code written by the authors of ansible-lint

import functools

from ansiblelater.rule import RuleBase

SORTER_TASKS = (
    "name",
    # "__module__",
    # "action",
    # "args",
    None,  # <-- None include all modules that not using action and *
    # "when",
    # "notify",
    # "tags",
    "block",
    "rescue",
    "always",
)


class CheckKeyOrder(RuleBase):
    rid = "ANS129"
    description = "Check for recommended key order"
    helptext = "{type} key order can be improved to `{sorted_keys}`"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        errors = []
        tasks, err = self.get_normalized_tasks(candidate, settings)

        if err:
            return self.Result(candidate.path, err)

        for task in tasks:
            is_sorted, keys = self._sort_keys(task.get("__raw_task__"))
            if not is_sorted:
                errors.append(
                    self.Error(
                        task["__line__"],
                        self.helptext.format(type="task", sorted_keys=", ".join(keys)),
                    )
                )

        if candidate.kind == "playbook":
            tasks, err = self.get_tasks(candidate, settings)

            if err:
                return self.Result(candidate.path, err)

            for task in tasks:
                is_sorted, keys = self._sort_keys(task)
                if not is_sorted:
                    errors.append(
                        self.Error(
                            task["__line__"],
                            self.helptext.format(type="play", sorted_keys=", ".join(keys)),
                        )
                    )

        return self.Result(candidate.path, errors)

    @staticmethod
    def _sort_keys(task):
        if not task:
            return True, []

        keys = [str(key) for key in task if not key.startswith("_")]
        sorted_keys = sorted(keys, key=functools.cmp_to_key(_task_property_sorter))

        return (keys == sorted_keys), sorted_keys


def _task_property_sorter(property1, property2):
    """Sort task properties based on SORTER."""
    v_1 = _get_property_sort_index(property1)
    v_2 = _get_property_sort_index(property2)
    return (v_1 > v_2) - (v_1 < v_2)


def _get_property_sort_index(name):
    """Return the index of the property in the sorter."""
    a_index = -1
    for i, v in enumerate(SORTER_TASKS):
        if v == name:
            return i
        if v is None:
            a_index = i
    return a_index
