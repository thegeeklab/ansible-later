import os

from ansiblelater.rule import RuleBase


class CheckCommandInsteadOfModule(RuleBase):
    rid = "ANS108"
    description = "Commands should not be used in place of modules"
    helptext = "{exec} command used in place of {module} module"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        commands = ["command", "shell", "raw"]
        modules = {
            "git": "git",
            "hg": "hg",
            "curl": "get_url or uri",
            "wget": "get_url or uri",
            "svn": "subversion",
            "service": "service",
            "mount": "mount",
            "rpm": "yum or rpm_key",
            "yum": "yum",
            "apt-get": "apt-get",
            "unzip": "unarchive",
            "tar": "unarchive",
            "chkconfig": "service",
            "rsync": "synchronize",
            "supervisorctl": "supervisorctl",
            "systemctl": "systemd",
            "sed": "template or lineinfile",
        }

        if not errors:
            for task in tasks:
                if task["action"]["__ansible_module__"] in commands:
                    first_cmd_arg = self.get_first_cmd_arg(task)
                    executable = os.path.basename(first_cmd_arg)
                    cmd = cmd = self.get_safe_cmd(task)

                    if (
                        first_cmd_arg
                        and executable in modules
                        and task["action"].get("warn", True)
                        and "register" not in task
                        and not any(ch in cmd for ch in self.SHELL_PIPE_CHARS)
                    ):
                        errors.append(
                            self.Error(
                                task["__line__"],
                                self.helptext.format(exec=executable, module=modules[executable]),
                            )
                        )

        return self.Result(candidate.path, errors)
