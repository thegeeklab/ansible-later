"""Review candidates."""

import codecs
import copy
import os

from ansible.plugins.loader import module_loader

from ansiblelater import LOG
from ansiblelater.logger import flag_extra
from ansiblelater.rule import RuleBase, SingleRules


class Candidate:
    """
    Meta object for all files which later has to process.

    Each file passed to later will be classified by type and
    bundled with necessary meta informations for rule processing.
    """

    def __init__(self, filename, settings={}, rules=[]):  # noqa
        self.path = filename
        self.binary = False
        self.vault = False
        self.filemeta = type(self).__name__.lower()
        self.kind = type(self).__name__.lower()
        self.faulty = False
        self.config = settings.config
        self.settings = settings

        try:
            with codecs.open(filename, mode="rb", encoding="utf-8") as f:
                if f.readline().startswith("$ANSIBLE_VAULT"):
                    self.vault = True
        except UnicodeDecodeError:
            self.binary = True

    def _filter_rules(self):
        target_rules = []
        includes = self.config["rules"]["include_filter"]
        excludes = self.config["rules"]["exclude_filter"]

        if len(includes) == 0:
            includes = [s.rid for s in self.rules]

        for rule in self.rules:
            if rule.rid in includes and rule.rid not in excludes:
                target_rules.append(rule)

        return target_rules

    def review(self):
        errors = 0
        self.rules = SingleRules(self.config["rules"]["dir"]).rules

        for rule in self._filter_rules():
            if self.kind not in rule.types:
                continue

            result = rule.check(self, self.config)

            if not result:
                LOG.error(f"rule '{rule.rid}' returns an empty result object. Check failed!")
                continue

            labels = {
                "tag": "review",
                "rule": rule.description,
                "file": self.path,
                "passed": True,
            }

            if rule.rid and rule.rid.strip():
                labels["rid"] = rule.rid

            for err in result.errors:
                err_labels = copy.copy(labels)
                err_labels["passed"] = False

                rid = self._format_id(rule.rid)
                path = self.path
                description = rule.description

                if isinstance(err, RuleBase.Error):
                    err_labels.update(err.to_dict())

                msg = f"{rid}rule '{description}' not met:\n{path}:{err}"

                if rule.rid not in self.config["rules"]["warning_filter"]:
                    LOG.error(msg, extra=flag_extra(err_labels))
                    errors = errors + 1
                else:
                    LOG.warning(msg, extra=flag_extra(err_labels))

        return errors

    @staticmethod
    def classify(filename, settings={}, rules=[]):  # noqa
        parentdir = os.path.basename(os.path.dirname(filename))
        basename = os.path.basename(filename)
        ext = os.path.splitext(filename)[1][1:]

        if parentdir in ["tasks"]:
            return Task(filename, settings, rules)
        if parentdir in ["handlers"]:
            return Handler(filename, settings, rules)
        if parentdir in ["vars", "defaults"]:
            return RoleVars(filename, settings, rules)
        if "group_vars" in filename.split(os.sep):
            return GroupVars(filename, settings, rules)
        if "host_vars" in filename.split(os.sep):
            return HostVars(filename, settings, rules)
        if parentdir in ["meta"] and "main" in basename:
            return Meta(filename, settings, rules)
        if parentdir in ["meta"] and "argument_specs" in basename:
            return ArgumentSpecs(filename, settings, rules)
        if parentdir in [
            "library",
            "lookup_plugins",
            "callback_plugins",
            "filter_plugins",
        ] or filename.endswith(".py"):
            return Code(filename, settings, rules)
        if basename == "inventory" or basename == "hosts" or parentdir in ["inventories"]:
            return Inventory(filename, settings, rules)
        if "rolesfile" in basename or ("requirements" in basename and ext in ["yaml", "yml"]):
            return Rolesfile(filename, settings, rules)
        if "Makefile" in basename:
            return Makefile(filename, settings, rules)
        if "templates" in filename.split(os.sep) or basename.endswith(".j2"):
            return Template(filename, settings, rules)
        if "files" in filename.split(os.sep):
            return File(filename, settings, rules)
        if basename.endswith(".yml") or basename.endswith(".yaml"):
            return Playbook(filename, settings, rules)
        if "README" in basename:
            return Doc(filename, settings, rules)
        return None

    def _format_id(self, rule_id):
        rid = rule_id.strip()
        if rid:
            rule_id = f"[{rid}] "

        return rule_id

    def __repr__(self):
        return f"{self.kind} ({self.path})"

    def __getitem__(self, item):
        return self.__dict__.get(item)


class RoleFile(Candidate):
    """Object classified as Ansible role file."""

    def __init__(self, filename, settings={}, rules=[]):  # noqa
        super().__init__(filename, settings, rules)

        parentdir = os.path.dirname(os.path.abspath(filename))
        while parentdir != os.path.dirname(parentdir):
            role_modules = os.path.join(parentdir, "library")
            if os.path.exists(role_modules):
                module_loader.add_directory(role_modules)
                break
            parentdir = os.path.dirname(parentdir)


class Playbook(Candidate):
    """Object classified as Ansible playbook."""

    pass


class Task(RoleFile):
    """Object classified as Ansible task file."""

    def __init__(self, filename, settings={}, rules=[]):  # noqa
        super().__init__(filename, settings, rules)
        self.filemeta = "tasks"


class Handler(RoleFile):
    """Object classified as Ansible handler file."""

    def __init__(self, filename, settings={}, rules=[]):  # noqa
        super().__init__(filename, settings, rules)
        self.filemeta = "handlers"


class Vars(Candidate):
    """Object classified as Ansible vars file."""

    pass


class InventoryVars(Candidate):
    """Object classified as Ansible inventory vars."""

    pass


class HostVars(InventoryVars):
    """Object classified as Ansible host vars."""

    pass


class GroupVars(InventoryVars):
    """Object classified as Ansible group vars."""

    pass


class RoleVars(RoleFile):
    """Object classified as Ansible role vars."""

    pass


class Meta(RoleFile):
    """Object classified as Ansible meta file."""

    pass


class ArgumentSpecs(RoleFile):
    """Object classified as Ansible roles argument specs file."""

    pass


class Inventory(Candidate):
    """Object classified as Ansible inventory file."""

    pass


class Code(Candidate):
    """Object classified as code file."""

    pass


class Template(RoleFile):
    """Object classified as Ansible template file."""

    pass


class Doc(Candidate):
    """Object classified as documentation file."""

    pass


class Makefile(Candidate):
    """Object classified as makefile."""

    pass


class File(RoleFile):
    """Object classified as generic file."""

    pass


class Rolesfile(Candidate):
    """Object classified as Ansible roles file."""

    pass
