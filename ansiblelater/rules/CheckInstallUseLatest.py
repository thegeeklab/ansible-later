from ansiblelater.rule import RuleBase


class CheckInstallUseLatest(RuleBase):
    rid = "ANS109"
    description = "Package installs should use present, not latest"
    helptext = "package installs should use `state=present` with or without a version"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        package_managers = [
            "yum",
            "apt",
            "dnf",
            "homebrew",
            "pacman",
            "openbsd_package",
            "pkg5",
            "portage",
            "pkgutil",
            "slackpkg",
            "swdepot",
            "zypper",
            "bundler",
            "pip",
            "pear",
            "npm",
            "yarn",
            "gem",
            "easy_install",
            "bower",
            "package",
            "apk",
            "openbsd_pkg",
            "pkgng",
            "sorcery",
            "xbps",
        ]

        if not errors:
            for task in tasks:
                if (
                    task["action"]["__ansible_module__"] in package_managers
                    and task["action"].get("state") == "latest"
                ):
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
