"""Review candidates."""

import codecs
import copy
import os
import re
from distutils.version import LooseVersion

from ansible.plugins.loader import module_loader

from ansiblelater import LOG
from ansiblelater import utils
from ansiblelater.logger import flag_extra
from ansiblelater.standard import SingleStandards
from ansiblelater.standard import StandardBase


class Candidate(object):
    """
    Meta object for all files which later has to process.

    Each file passed to later will be classified by type and
    bundled with necessary meta informations for rule processing.
    """

    def __init__(self, filename, settings={}, standards=[]):
        self.path = filename
        self.binary = False
        self.vault = False
        self.filetype = type(self).__name__.lower()
        self.expected_version = True
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

        if not version:
            version = utils.standards_latest(self.standards)
            if self.expected_version:
                if isinstance(self, RoleFile):
                    LOG.warning(
                        "{name} {path} is in a role that contains a meta/main.yml without a "
                        "declared standards version. "
                        "Using latest standards version {version}".format(
                            name=type(self).__name__, path=self.path, version=version
                        )
                    )
                else:
                    LOG.warning(
                        "{name} {path} does not present standards version. "
                        "Using latest standards version {version}".format(
                            name=type(self).__name__, path=self.path, version=version
                        )
                    )
        else:
            LOG.info(
                "{name} {path} declares standards version {version}".format(
                    name=type(self).__name__, path=self.path, version=version
                )
            )

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

    def review(self, lines=None):
        errors = 0
        self.standards = SingleStandards(self.config["rules"]["standards"]).rules
        self.version = self._get_version()

        for standard in self._filter_standards():
            if type(self).__name__.lower() not in standard.types:
                continue

            result = standard.check(self, self.config)

            if not result:
                LOG.error(
                    "Standard '{id}' returns an empty result object. Check failed!".format(
                        id=standard.sid
                    )
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
                if isinstance(err, StandardBase.Error):
                    err_labels.update(err.to_dict())

                if not standard.version:
                    LOG.warning(
                        "{sid}Best practice '{description}' not met:\n{path}:{error}".format(
                            sid=self._format_id(standard.sid),
                            description=standard.description,
                            path=self.path,
                            error=err
                        ),
                        extra=flag_extra(err_labels)
                    )
                elif LooseVersion(standard.version) > LooseVersion(self.version):
                    LOG.warning(
                        "{sid}Future standard '{description}' not met:\n{path}:{error}".format(
                            sid=self._format_id(standard.sid),
                            description=standard.description,
                            path=self.path,
                            error=err
                        ),
                        extra=flag_extra(err_labels)
                    )
                else:
                    LOG.error(
                        "{sid}Standard '{description}' not met:\n{path}:{error}".format(
                            sid=self._format_id(standard.sid),
                            description=standard.description,
                            path=self.path,
                            error=err
                        ),
                        extra=flag_extra(err_labels)
                    )
                    errors = errors + 1

        return errors

    @staticmethod
    def classify(filename, settings={}, standards=[]):
        parentdir = os.path.basename(os.path.dirname(filename))
        basename = os.path.basename(filename)

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
        if parentdir in ["meta"]:
            return Meta(filename, settings, standards)
        if (
            parentdir in ["library", "lookup_plugins", "callback_plugins", "filter_plugins"]
            or filename.endswith(".py")
        ):
            return Code(filename, settings, standards)
        if basename == "inventory" or basename == "hosts" or parentdir in ["inventories"]:
            return Inventory(filename, settings, standards)
        if "rolesfile" in basename or "requirements" in basename:
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
        if standard_id and standard_id.strip():
            standard_id = "[{id}] ".format(id=standard_id.strip())

        return standard_id

    def __repr__(self):  # noqa
        return "{name} ({path})".format(name=type(self).__name__, path=self.path)

    def __getitem__(self, item):  # noqa
        return self.__dict__.get(item)


class RoleFile(Candidate):
    """Object classified as Ansible role file."""

    def __init__(self, filename, settings={}, standards=[]):
        super(RoleFile, self).__init__(filename, settings, standards)

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

    def __init__(self, filename, settings={}, standards=[]):
        super(Task, self).__init__(filename, settings, standards)
        self.filetype = "tasks"


class Handler(RoleFile):
    """Object classified as Ansible handler file."""

    def __init__(self, filename, settings={}, standards=[]):
        super(Handler, self).__init__(filename, settings, standards)
        self.filetype = "handlers"


class Vars(Candidate):
    """Object classified as Ansible vars file."""

    pass


class Unversioned(Candidate):
    """Object classified as unversioned file."""

    def __init__(self, filename, settings={}, standards=[]):
        super(Unversioned, self).__init__(filename, settings, standards)
        self.expected_version = False


class InventoryVars(Unversioned):
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


class Inventory(Unversioned):
    """Object classified as Ansible inventory file."""

    pass


class Code(Unversioned):
    """Object classified as code file."""

    pass


class Template(RoleFile):
    """Object classified as Ansible template file."""

    pass


class Doc(Unversioned):
    """Object classified as documentation file."""

    pass


class Makefile(Unversioned):
    """Object classified as makefile."""

    pass


class File(RoleFile):
    """Object classified as generic file."""

    pass


class Rolesfile(Unversioned):
    """Object classified as Ansible roles file."""

    pass
