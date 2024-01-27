# Author: Adrián Tóth <adtoth@redhat.com>
#
# Copyright (c) 2020, Red Hat, Inc.
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


class CheckNestedJinja(RuleBase):
    rid = "ANS123"
    description = "Don't use nested Jinja2 pattern"
    helptext = (
        "there should not be any nested jinja pattern "
        "like `{{ list_one + {{ list_two | max }} }}`"
    )
    types = ["playbook", "task", "handler", "rolevars", "hostvars", "groupvars"]

    def check(self, candidate, settings):
        yamllines, errors = self.get_normalized_yaml(candidate, settings)
        pattern = re.compile(r"{{(?:[^{}]*)?[^'\"]{{")
        matches = []

        if not errors:
            for i, line in yamllines:
                if "!unsafe" in line:
                    continue

                match = pattern.findall(line)
                if match:
                    for item in match:
                        matches.append((i, item))

            for i, _ in matches:
                errors.append(self.Error(i, self.helptext))

        return self.Result(candidate.path, errors)
