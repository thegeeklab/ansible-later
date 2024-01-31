# Original code written by the authors of ansible-lint

from ansiblelater.rule import RuleBase
from ansiblelater.utils import load_plugin


class CheckFQCNBuiltin(RuleBase):
    rid = "ANS128"
    helptext = "use FQCN `{module_alias}` for module action `{module}`"
    description = "Module actions should use full qualified collection names"
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars"]
    module_aliases = {"block/always/rescue": "block/always/rescue"}

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)

        _builtins = [
            "add_host",
            "apt",
            "apt_key",
            "apt_repository",
            "assemble",
            "assert",
            "async_status",
            "blockinfile",
            "command",
            "copy",
            "cron",
            "debconf",
            "debug",
            "dnf",
            "dpkg_selections",
            "expect",
            "fail",
            "fetch",
            "file",
            "find",
            "gather_facts",
            "get_url",
            "getent",
            "git",
            "group",
            "group_by",
            "hostname",
            "import_playbook",
            "import_role",
            "import_tasks",
            "include",
            "include_role",
            "include_tasks",
            "include_vars",
            "iptables",
            "known_hosts",
            "lineinfile",
            "meta",
            "package",
            "package_facts",
            "pause",
            "ping",
            "pip",
            "raw",
            "reboot",
            "replace",
            "rpm_key",
            "script",
            "service",
            "service_facts",
            "set_fact",
            "set_stats",
            "setup",
            "shell",
            "slurp",
            "stat",
            "subversion",
            "systemd",
            "sysvinit",
            "tempfile",
            "template",
            "unarchive",
            "uri",
            "user",
            "wait_for",
            "wait_for_connection",
            "yum",
            "yum_repository",
        ]

        if errors:
            return self.Result(candidate.path, errors)

        for task in tasks:
            module = task["action"]["__ansible_module_original__"]

            if module not in self.module_aliases:
                loaded_module = load_plugin(module)
                target = loaded_module.resolved_fqcn
                self.module_aliases[module] = target

                if target is None:
                    self.module_aliases[module] = module
                    continue

                if target not in self.module_aliases:
                    self.module_aliases[target] = target

            if module != self.module_aliases[module]:
                module_alias = self.module_aliases[module]
                if module_alias.startswith("ansible.builtin"):
                    legacy_module = module_alias.replace(
                        "ansible.builtin.",
                        "ansible.legacy.",
                        1,
                    )
                    if module != legacy_module:
                        helptext = self.helptext.format(module_alias=module_alias, module=module)
                        if module == "ansible.builtin.include":
                            helptext = (
                                "`ansible.builtin.include_task` or `ansible.builtin.import_tasks` "
                                f"should be used instead of deprecated `{module}`",
                            )

                        errors.append(self.Error(task["__line__"], helptext))
                else:
                    if module.count(".") < 2:
                        errors.append(
                            self.Error(
                                task["__line__"],
                                self.helptext.format(module_alias=module_alias, module=module),
                            )
                        )

        return self.Result(candidate.path, errors)
