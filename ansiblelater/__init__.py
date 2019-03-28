"""Default package."""

__author__ = "Robert Kaussow"
__project__ = "ansible-later"
__version__ = "0.1.5"
__license__ = "MIT"
__maintainer__ = "Robert Kaussow"
__email__ = "mail@geeklabor.de"
__status__ = "Production"

import codecs
import os
import re
from distutils.version import LooseVersion

import ansible
from appdirs import AppDirs

from . import logger
from .settings import Settings
from ansiblelater.utils import (get_property,
                                is_line_in_ranges, lines_ranges,
                                read_standards, standards_latest)

try:
    # Ansible 2.4 import of module loader
    from ansible.plugins.loader import module_loader
except ImportError:
    try:
        from ansible.plugins import module_loader
    except ImportError:
        from ansible.utils import module_finder as module_loader

settings = Settings()
logger = logger.get_logger(__name__, settings.config["logging"]["level"])


class Standard(object):
    """
    Standard definition for all defined rules.

    Later lookup the config file for a path to a rules directory
    or fallback to default `ansiblelater/examples/*`.
    """

    def __init__(self, standard_dict):
        """
        Initialize a new standard object and returns None.

        :param standard_dict: Dictionary object containing all neseccary attributes
        """
        if "id" not in standard_dict:
            standard_dict.update(id="")
        else:
            standard_dict.update(id="[{}] ".format(standard_dict.get("id")))

        self.id = standard_dict.get("id")
        self.name = standard_dict.get("name")
        self.version = standard_dict.get("version")
        self.check = standard_dict.get("check")
        self.types = standard_dict.get("types")

    def __repr__(self): # noqa
        return "Standard: %s (version: %s, types: %s)" % (
               self.name, self.version, self.types)


class Candidate(object):
    """
    Meta object for all files which later has to process.

    Each file passed to later will be classified by type and
    bundled with necessary meta informations for rule processing.
    """

    def __init__(self, filename):
        self.path = filename
        self.binary = False
        self.vault = False

        try:
            self.version = find_version(filename)
            with codecs.open(filename, mode="rb", encoding="utf-8") as f:
                if f.readline().startswith("$ANSIBLE_VAULT"):
                    self.vault = True
        except UnicodeDecodeError:
            self.binary = True

        self.filetype = type(self).__name__.lower()
        self.expected_version = True

    def review(self, settings, lines=None):
        return candidate_review(self, settings, lines)

    def __repr__(self): # noqa
        return "%s (%s)" % (type(self).__name__, self.path)

    def __getitem__(self, item): # noqa
        return self.__dict__.get(item)


class Error(object):
    """Default error object created if a rule failed."""

    def __init__(self, lineno, message):
        """
        Initialize a new error object and returns None.

        :param lineno: Line number where the error from de rule occures
        :param message: Detailed error description provided by the rule
        """
        self.lineno = lineno
        self.message = message

    def __repr__(self): # noqa
        if self.lineno:
            return "%s: %s" % (self.lineno, self.message)
        else:
            return " %s" % (self.message)


class Result(object):
    def __init__(self, candidate, errors=None):
        self.candidate = candidate
        self.errors = errors or []

    def message(self):
        return "\n".join(["{0}:{1}".format(self.candidate, error)
                          for error in self.errors])


class RoleFile(Candidate):
    def __init__(self, filename):
        super(RoleFile, self).__init__(filename)
        self.version = None
        parentdir = os.path.dirname(os.path.abspath(filename))
        while parentdir != os.path.dirname(parentdir):
            meta_file = os.path.join(parentdir, "meta", "main.yml")
            if os.path.exists(meta_file):
                self.version = find_version(meta_file)
                if self.version:
                    break
            parentdir = os.path.dirname(parentdir)
        role_modules = os.path.join(parentdir, "library")
        if os.path.exists(role_modules):
            module_loader.add_directory(role_modules)


class Playbook(Candidate):
    pass


class Task(RoleFile):
    def __init__(self, filename):
        super(Task, self).__init__(filename)
        self.filetype = "tasks"


class Handler(RoleFile):
    def __init__(self, filename):
        super(Handler, self).__init__(filename)
        self.filetype = "handlers"


class Vars(Candidate):
    pass


class Unversioned(Candidate):
    def __init__(self, filename):
        super(Unversioned, self).__init__(filename)
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


# For ease of checking files for tabs
class Makefile(Unversioned):
    pass


class File(RoleFile):
    pass


class Rolesfile(Unversioned):
    pass


def classify(filename):
    parentdir = os.path.basename(os.path.dirname(filename))

    if parentdir in ["tasks"]:
        return Task(filename)
    if parentdir in ["handlers"]:
        return Handler(filename)
    if parentdir in ["vars", "defaults"]:
        return RoleVars(filename)
    if "group_vars" in filename.split(os.sep):
        return GroupVars(filename)
    if "host_vars" in filename.split(os.sep):
        return HostVars(filename)
    if parentdir in ["meta"]:
        return Meta(filename)
    if parentdir in ["library", "lookup_plugins", "callback_plugins",
                     "filter_plugins"] or filename.endswith(".py"):
        return Code(filename)
    if "inventory" in filename or "hosts" in filename or parentdir in ["inventory"]:
        return Inventory(filename)
    if "rolesfile" in filename or "requirements" in filename:
        return Rolesfile(filename)
    if "Makefile" in filename:
        return Makefile(filename)
    if "templates" in filename.split(os.sep) or filename.endswith(".j2"):
        return Template(filename)
    if "files" in filename.split(os.sep):
        return File(filename)
    if filename.endswith(".yml") or filename.endswith(".yaml"):
        return Playbook(filename)
    if "README" in filename:
        return Doc(filename)
    return None


def candidate_review(candidate, settings, lines=None):
    errors = 0
    standards = read_standards(settings)
    if getattr(standards, "ansible_min_version", None) and \
            LooseVersion(standards.ansible_min_version) > LooseVersion(ansible.__version__):
        raise SystemExit("Standards require ansible version %s (current version %s). "
                         "Please upgrade ansible." %
                         (standards.ansible_min_version, ansible.__version__))

    if getattr(standards, "ansible_review_min_version", None) and \
            LooseVersion(standards.ansible_review_min_version) > LooseVersion(
                get_property("__version__")):
        raise SystemExit("Standards require ansible-later version %s (current version %s). "
                         "Please upgrade ansible-later." %
                         (standards.ansible_review_min_version, get_property("__version__")))

    if not candidate.version:
        candidate.version = standards_latest(standards.standards)
        if candidate.expected_version:
            if isinstance(candidate, RoleFile):
                logger.warn("%s %s is in a role that contains a meta/main.yml without a declared "
                            "standards version. "
                            "Using latest standards version %s" %
                            (type(candidate).__name__, candidate.path, candidate.version),
                            settings)
            else:
                logger.warn("%s %s does not present standards version. "
                            "Using latest standards version %s" %
                            (type(candidate).__name__, candidate.path, candidate.version),
                            settings)

    info("%s %s declares standards version %s" %
         (type(candidate).__name__, candidate.path, candidate.version),
         settings)

    for standard in standards.standards:
        print(type(standard))
        if type(candidate).__name__.lower() not in standard.types:
            continue
        if settings.standards_filter and standard.name not in settings.standards_filter:
            continue
        result = standard.check(candidate, settings)

        if not result:
            abort("Standard '%s' returns an empty result object." %
                  (standard.check.__name__))

        for err in [err for err in result.errors
                    if not err.lineno or is_line_in_ranges(err.lineno, lines_ranges(lines))]:
            if not standard.version:
                warn("{id}Best practice '{name}' not met:\n{path}:{error}".format(
                    id=standard.id, name=standard.name, path=candidate.path, error=err), settings)
            elif LooseVersion(standard.version) > LooseVersion(candidate.version):
                warn("{id}Future standard '{name}' not met:\n{path}:{error}".format(
                    id=standard.id, name=standard.name, path=candidate.path, error=err), settings)
            else:
                error("{id}Standard '{name}' not met:\n{path}:{error}".format(
                    id=standard.id, name=standard.name, path=candidate.path, error=err))
                errors = errors + 1
        if not result.errors:
            if not standard.version:
                info("Best practice '%s' met" % standard.name, settings)
            elif LooseVersion(standard.version) > LooseVersion(candidate.version):
                info("Future standard '%s' met" % standard.name, settings)
            else:
                info("Standard '%s' met" % standard.name, settings)

    return errors


def find_version(filename, version_regex=r"^# Standards:\s*([\d.]+)"):
    version_re = re.compile(version_regex)

    with codecs.open(filename, mode="rb", encoding="utf-8") as f:
        for line in f:
            match = version_re.match(line)
            if match:
                return match.group(1)
    return None
