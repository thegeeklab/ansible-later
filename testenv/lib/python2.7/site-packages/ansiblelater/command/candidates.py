"""Review candidates."""

import codecs
import copy
import os
import re
from distutils.version import LooseVersion

from six import iteritems

from ansiblelater import LOG
from ansiblelater import utils
from ansiblelater.logger import flag_extra

try:
    # Ansible 2.4 import of module loader
    from ansible.plugins.loader import module_loader
except ImportError:
    try:
        from ansible.plugins import module_loader
    except ImportError:
        from ansible.utils import module_finder as module_loader


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
        self.standards = self._get_standards(settings, standards)

        try:
            with codecs.open(filename, mode="rb", encoding="utf-8") as f:
                if f.readline().startswith("$ANSIBLE_VAULT"):
                    self.vault = True
        except UnicodeDecodeError:
            self.binary = True

        self.version = self._get_version(settings)

    def _get_version(self, settings):
        path = self.path
        version = None

        if not self.binary:
            if isinstance(self, RoleFile):
                parentdir = os.path.dirname(os.path.abspath(self.path))
                while parentdir != os.path.dirname(parentdir):
                    meta_file = os.path.join(parentdir, "meta", "main.yml")
                    if os.path.exists(meta_file):
                        path = meta_file
                        break
                    parentdir = os.path.dirname(parentdir)

            version_re = re.compile(r"^# Standards:\s*([\d.]+)")

            with codecs.open(path, mode="rb", encoding="utf-8") as f:
                for line in f:
                    match = version_re.match(line)
                    if match:
                        version = match.group(1)

        if not version:
            version = utils.standards_latest(self.standards)
            if self.expected_version:
                if isinstance(self, RoleFile):
                    LOG.warning(
                        "%s %s is in a role that contains a meta/main.yml without a declared "
                        "standards version. "
                        "Using latest standards version %s" %
                        (type(self).__name__, self.path, version))
                else:
                    LOG.warning(
                        "%s %s does not present standards version. "
                        "Using latest standards version %s" %
                        (type(self).__name__, self.path, version))
        else:
            LOG.info("%s %s declares standards version %s" %
                     (type(self).__name__, self.path, version))

        return version

    def _get_standards(self, settings, standards):
        target_standards = []
        includes = settings.config["rules"]["filter"]
        excludes = settings.config["rules"]["exclude_filter"]

        if len(includes) == 0:
            includes = [s.id for s in standards]

        for standard in standards:
            if standard.id in includes and standard.id not in excludes:
                target_standards.append(standard)

        return target_standards

    def review(self, settings, lines=None):
        errors = 0

        for standard in self.standards:
            if type(self).__name__.lower() not in standard.types:
                continue

            result = standard.check(self, settings.config)

            if not result:
                utils.sysexit_with_message("Standard '{}' returns an empty result object.".format(
                    standard.check.__name__))

            labels = {"tag": "review", "standard": standard.name, "file": self.path, "passed": True}

            if standard.id and standard.id.strip():
                labels["id"] = standard.id

            for err in [err for err in result.errors
                        if not err.lineno or utils.is_line_in_ranges(err.lineno, utils.lines_ranges(lines))]: # noqa
                err_labels = copy.copy(labels)
                err_labels["passed"] = False
                if isinstance(err, Error):
                    err_labels.update(err.to_dict())

                if not standard.version:
                    LOG.warning("{id}Best practice '{name}' not met:\n{path}:{error}".format(
                        id=self._format_id(standard.id),
                        name=standard.name,
                        path=self.path,
                        error=err), extra=flag_extra(err_labels))
                elif LooseVersion(standard.version) > LooseVersion(self.version):
                    LOG.warning("{id}Future standard '{name}' not met:\n{path}:{error}".format(
                        id=self._format_id(standard.id),
                        name=standard.name,
                        path=self.path,
                        error=err), extra=flag_extra(err_labels))
                else:
                    LOG.error("{id}Standard '{name}' not met:\n{path}:{error}".format(
                        id=self._format_id(standard.id),
                        name=standard.name,
                        path=self.path,
                        error=err), extra=flag_extra(err_labels))
                    errors = errors + 1

        return errors

    def _format_id(self, standard_id):
        if standard_id and standard_id.strip():
            standard_id = "[{id}] ".format(id=standard_id.strip())

        return standard_id

    def __repr__(self): # noqa
        return "%s (%s)" % (type(self).__name__, self.path)

    def __getitem__(self, item): # noqa
        return self.__dict__.get(item)


class RoleFile(Candidate):
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
    pass


class Task(RoleFile):
    def __init__(self, filename, settings={}, standards=[]):
        super(Task, self).__init__(filename, settings, standards)
        self.filetype = "tasks"


class Handler(RoleFile):
    def __init__(self, filename, settings={}, standards=[]):
        super(Handler, self).__init__(filename, settings, standards)
        self.filetype = "handlers"


class Vars(Candidate):
    pass


class Unversioned(Candidate):
    def __init__(self, filename, settings={}, standards=[]):
        super(Unversioned, self).__init__(filename, settings, standards)
        self.expected_version = False


class InventoryVars(Unversioned):
    pass


class HostVars(InventoryVars):
    pass


class GroupVars(InventoryVars):
    pass


class RoleVars(RoleFile):
    pass


class Meta(RoleFile):
    pass


class Inventory(Unversioned):
    pass


class Code(Unversioned):
    pass


class Template(RoleFile):
    pass


class Doc(Unversioned):
    pass


class Makefile(Unversioned):
    pass


class File(RoleFile):
    pass


class Rolesfile(Unversioned):
    pass


class Error(object):
    """Default error object created if a rule failed."""

    def __init__(self, lineno, message, error_type=None, **kwargs):
        """
        Initialize a new error object and returns None.

        :param lineno: Line number where the error from de rule occures
        :param message: Detailed error description provided by the rule

        """
        self.lineno = lineno
        self.message = message
        self.kwargs = kwargs
        for (key, value) in iteritems(kwargs):
            setattr(self, key, value)

    def __repr__(self): # noqa
        if self.lineno:
            return "%s: %s" % (self.lineno, self.message)
        else:
            return " %s" % (self.message)

    def to_dict(self):
        result = dict(lineno=self.lineno, message=self.message)
        for (key, value) in iteritems(self.kwargs):
            result[key] = value
        return result


class Result(object):
    def __init__(self, candidate, errors=None):
        self.candidate = candidate
        self.errors = errors or []

    def message(self):
        return "\n".join(["{0}:{1}".format(self.candidate, error)
                          for error in self.errors])


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
    if parentdir in ["library", "lookup_plugins", "callback_plugins",
                     "filter_plugins"] or filename.endswith(".py"):
        return Code(filename, settings, standards)
    if "inventory" == basename or "hosts" == basename or parentdir in ["inventories"]:
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
