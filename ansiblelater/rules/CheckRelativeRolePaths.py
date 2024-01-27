# Copyright (c) 2016, Tsukinowa Inc. <info@tsukinowa.jp>
# Copyright (c) 2018, Ansible Project
from ansiblelater.rule import RuleBase


class CheckRelativeRolePaths(RuleBase):
    rid = "ANS125"
    description = "Don't use a relative path in a role"
    helptext = "`copy` and `template` modules don't need relative path for `src`"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        module_to_path_folder = {
            "copy": "files",
            "win_copy": "files",
            "template": "templates",
            "win_template": "win_templates",
        }

        if not errors:
            for task in tasks:
                module = task["action"]["__ansible_module__"]
                path_to_check = None

                if module in module_to_path_folder and "src" in task["action"]:
                    path_to_check = f"../{module_to_path_folder[module]}"

                if path_to_check and path_to_check in task["action"]["src"]:
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
