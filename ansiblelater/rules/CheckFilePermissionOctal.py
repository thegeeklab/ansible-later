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

from ansiblelater.rule import RuleBase


class CheckFilePermissionOctal(RuleBase):
    rid = "ANS119"
    description = "Numeric file permissions without a leading zero can behave unexpectedly"
    helptext = '`mode: {mode}` should be strings with a leading zero `mode: "0{mode}"`'
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        modules = [
            "assemble",
            "copy",
            "file",
            "ini_file",
            "lineinfile",
            "replace",
            "synchronize",
            "template",
            "unarchive",
        ]

        if not errors:
            for task in tasks:
                if task["action"]["__ansible_module__"] in modules:
                    mode = task["action"].get("mode", None)

                    if isinstance(mode, int) and self._is_invalid_permission(mode):
                        errors.append(
                            self.Error(task["__line__"], self.helptext.format(mode=mode))
                        )

        return self.Result(candidate.path, errors)

    @staticmethod
    def _is_invalid_permission(mode):
        other_write_without_read = (
            mode % 8 and mode % 8 < 4 and not (mode % 8 == 1 and (mode >> 6) % 2 == 1)
        )
        group_write_without_read = (
            (mode >> 3) % 8
            and (mode >> 3) % 8 < 4
            and not ((mode >> 3) % 8 == 1 and (mode >> 6) % 2 == 1)
        )
        user_write_without_read = (mode >> 6) % 8 and (mode >> 6) % 8 < 4 and (mode >> 6) % 8 != 1
        other_more_generous_than_group = mode % 8 > (mode >> 3) % 8
        other_more_generous_than_user = mode % 8 > (mode >> 6) % 8
        group_more_generous_than_user = (mode >> 3) % 8 > (mode >> 6) % 8

        return bool(
            other_write_without_read
            or group_write_without_read
            or user_write_without_read
            or other_more_generous_than_group
            or other_more_generous_than_user
            or group_more_generous_than_user
        )
