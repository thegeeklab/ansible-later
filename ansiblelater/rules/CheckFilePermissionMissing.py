# Copyright (c) 2020 Sorin Sbarnea <sorin.sbarnea@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import re

from ansiblelater.rule import RuleBase


class CheckFilePermissionMissing(RuleBase):
    rid = "ANS118"
    description = "File permissions unset or incorrect"
    helptext = (
        "`mode` parameter should set permissions explicitly (e.g. `mode: 0644`) "
        "to avoid unexpected file permissions"
    )
    types = ["playbook", "task", "handler"]

    _modules = {
        "archive",
        "assemble",
        "copy",
        "file",
        "replace",
        "template",
    }
    _create_modules = {
        "blockinfile": False,
        "htpasswd": True,
        "ini_file": True,
        "lineinfile": False,
    }
    _preserve_modules = (
        "copy",
        "template",
    )

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)

        if not errors:
            for task in tasks:
                if self._check_mode(task):
                    errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)

    def _check_mode(self, task):
        module = task["action"]["__ansible_module__"]
        mode = task["action"].get("mode", None)
        state = task["action"].get("state", "file")

        if module not in self._modules and module not in self._create_modules:
            return False

        if mode == "preserve" and module not in self._preserve_modules:
            return True

        if module in self._create_modules:
            create = task["action"].get("create", self._create_modules[module])
            return create and mode is None

        # If Jinja syntax is used state can not be validated
        jinja = re.compile("{{(.*?)}}")
        if jinja.findall(state):
            return False

        # A file that doesn't exist cannot have a mode
        if state == "absent":
            return False

        # A symlink always has mode 0o777
        if state == "link":
            return False

        # Recurse on a directory does not allow for an uniform mode
        if task["action"].get("recurse", None):
            return False

        # The file module does not create anything when state==file (default)
        if module == "file" and state == "file":
            return False

        # replace module is the only one that has a valid default preserve
        # behavior, but we want to trigger rule if user used incorrect
        # documentation and put "preserve", which is not supported.
        if module == "replace" and mode is None:
            return False

        return mode is None
