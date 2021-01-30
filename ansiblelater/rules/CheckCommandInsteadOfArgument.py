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

from ansiblelater.standard import StandardBase


class CheckCommandInsteadOfArgument(StandardBase):

    sid = "ANSIBLE0017"
    description = "Commands should not be used in place of module arguments"
    helptext = "{exec} used in place of file modules argument {arg}"
    version = "0.2"
    types = ["playbook", "task", "handler"]

    def check(self, candidate, settings):
        tasks, errors = self.get_normalized_tasks(candidate, settings)
        commands = ["command", "shell", "raw"]
        arguments = {
            "chown": "owner",
            "chmod": "mode",
            "chgrp": "group",
            "ln": "state=link",
            "mkdir": "state=directory",
            "rmdir": "state=absent",
            "rm": "state=absent"
        }

        if not errors:
            for task in tasks:
                if task["action"]["__ansible_module__"] in commands:
                    first_cmd_arg = self.get_first_cmd_arg(task)
                    executable = os.path.basename(first_cmd_arg)

                    if (
                        first_cmd_arg and executable in arguments
                        and task["action"].get("warn", True)
                    ):
                        errors.append(
                            self.Error(
                                task["__line__"],
                                self.helptext.format(exec=executable, arg=arguments[executable])
                            )
                        )

        return self.Result(candidate.path, errors)
