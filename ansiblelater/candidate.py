"""Review candidates."""

import codecs
import copy
import os
import re

from ansible.plugins.loader import module_loader
from packaging.version import Version

from ansiblelater import LOG, utils
from ansiblelater.logger import flag_extra
from ansiblelater.standard import SingleStandards, StandardBase


class Candidate:
    """
    Meta object for all files which later has to process.

    Each file passed to later will be classified by type and
    bundled with necessary meta informations for rule processing.
    """

    def __init__(self, filename, settings={}, standards=[]):  # noqa
        self.path = filename
        self.binary = False
        self.vault = False
        self.filetype = type(self).__name__.lower()
        self.faulty = False
        self.config = settings.config
        self.settings = settings

        try:
            with codecs.open(filename, mode="rb", encoding="utf-8") as f:
                if f.readline().startswith("$ANSIBLE_VAULT"):
                    self.vault = True
        except UnicodeDecodeError:
            self.binary = True

    def _get_version(self):
        name = type(self).__name__
        path = self.path
        version = None
        config_version = self.config["rules"]["version"].strip()

        if config_version:
            version_config_re = re.compile(r"([\d.]+)")
            match = version_config_re.match(config_version)
            if match:
                version = match.group(1)

        if not self.binary:
            if isinstance(self, RoleFile):
                parentdir = os.path.dirname(os.path.abspath(self.path))
                while parentdir != os.path.dirname(parentdir):
                    meta_file = os.path.join(parentdir, "meta", "main.yml")
                    if os.path.exists(meta_file):
                        path = meta_file
                        break
                    parentdir = os.path.dirname(parentdir)

            version_file_re = re.compile(r"^# Standards:\s*([\d.]+)")
            with codecs.open(path, mode="rb", encoding="utf-8") as f:
                for line in f:
                    match = version_file_re.match(line)
                    if match:
                        version = match.group(1)

        if version:
            LOG.info(f"{name} {path} declares standards version {version}")

        return version

    def _filter_standards(self):
        target_standards = []
        includes = self.config["rules"]["filter"]
        excludes = self.config["rules"]["exclude_filter"]

        if len(includes) == 0:
            includes = [s.sid for s in self.standards]

        for standard in self.standards:
            if standard.sid in includes and standard.sid not in excludes:
                target_standards.append(standard)

        return target_standards

    def review(self):
        errors = 0
        self.standards = SingleStandards(self.config["rules"]["standards"]).rules
        self.version_config = self._get_version()
        self.version = self.version_config or utils.standards_latest(self.standards)

        for standard in self._filter_standards():
            if type(self).__name__.lower() not in standard.types:
                continue

            result = standard.check(self, self.config)

            if not result:
                LOG.error(
                    f"Standard '{standard.sid}' returns an empty result object. Check failed!"
                )
                continue

            labels = {
                "tag": "review",
                "standard": standard.description,
                "file": self.path,
                "passed": True
            }

            if standard.sid and standard.sid.strip():
                labels["sid"] = standard.sid

            for err in result.errors:
                err_labels = copy.copy(labels)
                err_labels["passed"] = False

                sid = self._format_id(standard.sid)
                path = self.path
                description = standard.description

                if isinstance(err, StandardBase.Error):
                    err_labels.update(err.to_dict())

                if not standard.version:
                    LOG.warning(
                        f"{sid}Best practice '{description}' not met:\n{path}:{err}",
                        extra=flag_extra(err_labels)
                    )
                elif Version(standard.version) > Version(self.version):
                    LOG.warning(
                        f"{sid}Future standard '{description}' not met:\n{path}:{err}",
                        extra=flag_extra(err_labels)
                    )
                else:
                    msg = f"{sid}Standard '{description}' not met:\n{path}:{err}"

                    if standard.sid not in self.config["rules"]["warning_filter"]:
                        LOG.error(msg, extra=flag_extra(err_labels))
                        errors = errors + 1
                    else:
                        LOG.warning(msg, extra=flag_extra(err_labels))

        return errors

    @staticmethod
    def classify(filename, settings={}, standards=[]):  # noqa
        parentdir = os.path.basename(os.path.dirname(filename))
        basename = os.path.basename(filename)
        ext = os.path.splitext(filename)[1][1:]

        if parentdir in ["tasks"]:
            return Task(filename, settings, standards)
        if parentdir in ["handlers"]:
            return Handler(filename, settings, standards)
        if parentdir in ["vars", "defaults"]:
            return RoleVars(filename, settings, standards)
        if "group_vars" in filename.split(os.sep):
            return GroupVars(filename, settings, standards)
        if "host_vars" in filename.split(os.sep):
            return HostVars(filename, settings, standards)
        if parentdir in ["meta"] and "main" in basename:
            return Meta(filename, settings, standards)
        if parentdir in ["meta"] and "argument_specs" in basename:
            return ArgumentSpecs(filename, settings, standards)
        if (
            parentdir in ["library", "lookup_plugins", "callback_plugins", "filter_plugins"]
            or filename.endswith(".py")
        ):
            return Code(filename, settings, standards)
        if basename == "inventory" or basename == "hosts" or parentdir in ["inventories"]:
            return Inventory(filename, settings, standards)
        if ("rolesfile" in basename or ("requirements" in basename and ext in ["yaml", "yml"])):
            return Rolesfile(filename, settings, standards)
        if "Makefile" in basename:
            return Makefile(filename, settings, standards)
        if "templates" in filename.split(os.sep) or basename.endswith(".j2"):
            return Template(filename, settings, standards)
        if "files" in filename.split(os.sep):
            return File(filename, settings, standards)
        if basename.endswith(".yml") or basename.endswith(".yaml"):
            return Playbook(filename, settings, standards)
        if "README" in basename:
            return Doc(filename, settings, standards)
        return None

    def _format_id(self, standard_id):
        sid = standard_id.strip()
        if sid:
            standard_id = f"[{sid}] "

        return standard_id

    def __repr__(self):
        return f"{type(self).__name__} ({self.path})"

    def __getitem__(self, item):
        return self.__dict__.get(item)


class RoleFile(Candidate):
    """Object classified as Ansible role file."""

    def __init__(self, filename, settings={}, standards=[]):  # noqa
        super().__init__(filename, settings, standards)

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

    def __init__(self, filename, settings={}, standards=[]):  # noqa
        super().__init__(filename, settings, standards)
        self.filetype = "tasks"


class Handler(RoleFile):
    """Object classified as Ansible handler file."""

    def __init__(self, filename, settings={}, standards=[]):  # noqa
        super().__init__(filename, settings, standards)
        self.filetype = "handlers"


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
