# Copyright (c) 2016 Will Thames <will@thames.id.au>
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

from ansiblelater.rule import RuleBase


class CheckChangedInWhen(RuleBase):
    rid = "ANS126"
    description = "Use handlers instead of `when: changed`"
    helptext = "tasks using `when: result.changed` setting are effectively acting as a handler"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)

        if not errors:
            for task in tasks:
                when = None

                if task["__ansible_action_type__"] in ["task", "meta"]:
                    when = task.get("when")

                if isinstance(when, str):
                    when = [when]

                if isinstance(when, list):
                    for item in when:
                        if self._changed_in_when(item):
                            errors.append(self.Error(task["__line__"], self.helptext))

        return self.Result(candidate.path, errors)

    @staticmethod
    def _changed_in_when(item):
        if not isinstance(item, str):
            return False

        if not {"and", "or", "not"}.isdisjoint(item.split()):
            return False

        return any(
            changed in item
            for changed in [
                ".changed",
                "|changed",
                '["changed"]',
                "['changed']",
                "is changed",
            ]
        )
