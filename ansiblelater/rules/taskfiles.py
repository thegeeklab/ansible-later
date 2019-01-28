import re

from collections import defaultdict

from ansiblelater import Error, Result
from ansiblelater.utils.rulehelper import get_normalized_yaml


def check_line_between_tasks(candidate, settings):
    options = defaultdict(dict)
    options.update(remove_empty=False)
    options.update(remove_markers=False)

    lines, errors = get_normalized_yaml(candidate, settings, options)
    description = "missing task separation (required: 1 empty line)"

    task_regex = re.compile(r"-\sname:.*")
    prevline = "#file_start_marker"

    allowed_prevline = ["---", "tasks:", "pre_tasks:", "post_tasks:", "block:"]

    if not errors:
        for i, line in lines:
            match = task_regex.search(line)
            if match and prevline:
                if not any(item in prevline for item in allowed_prevline):
                    errors.append(Error(i, description))
            prevline = line.strip()

    return Result(candidate.path, errors)
