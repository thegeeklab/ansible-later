# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
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

import os

from ansiblelater.rule import RuleBase
from ansiblelater.utils import has_glob, has_jinja


class CheckDeprecatedBareVars(RuleBase):
    rid = "ANS127"
    description = "Deprecated bare variables in loops must not be used"
    helptext = (
        "bare var '{barevar}' in '{loop_type}' must use full var syntax '{{{{ {barevar} }}}}' "
        "or be converted to a list"
    )
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, self.errors = self.get_normalized_tasks(candidate, settings)

        if not self.errors:
            for task in tasks:
                loop_type = next((key for key in task if key.startswith("with_")), None)

                if not loop_type:
                    continue

                if loop_type in [
                    "with_nested",
                    "with_together",
                    "with_flattened",
                    "with_filetree",
                    "with_community.general.filetree",
                ]:
                    # These loops can either take a list defined directly in the task
                    # or a variable that is a list itself.  When a single variable is used
                    # we just need to check that one variable, and not iterate over it like
                    # it's a list. Otherwise, loop through and check all items.
                    items = task[loop_type]

                    if not isinstance(items, (list, tuple)):
                        items = [items]
                    for var in items:
                        self._matchvar(var, task, loop_type)
                elif loop_type == "with_subelements":
                    self._matchvar(task[loop_type][0], task, loop_type)
                elif loop_type in ["with_sequence", "with_ini", "with_inventory_hostnames"]:
                    pass
                else:
                    self._matchvar(task[loop_type], task, loop_type)

        return self.Result(candidate.path, self.errors)

    def _matchvar(self, varstring, task, loop_type):
        if isinstance(varstring, str) and not has_jinja(varstring):
            valid = loop_type == "with_fileglob" and bool(
                has_jinja(varstring) or has_glob(varstring),
            )

            valid |= loop_type == "with_filetree" and bool(
                has_jinja(varstring) or varstring.endswith(os.sep),
            )
            if not valid:
                self.errors.append(
                    self.Error(
                        task["__line__"],
                        self.helptext.format(barevar=varstring, loop_type=loop_type),
                    )
                )
