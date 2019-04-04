"""Custom exceptions."""

import re


class LaterError(Exception):
    """Generic exception for later."""

    def __init__(self, msg, original):
        """Initialize new exception."""
        super(LaterError, self).__init__(msg + (": %s" % original))
        self.original = original


class LaterAnsibleError(Exception):
    """Wrapper for ansible syntax errors."""

    def __init__(self, msg, original):
        lines = original.message.splitlines()

        line_no = re.search("line(.*?),", lines[2])
        column_no = re.search("column(.*?),", lines[2])

        self.message = lines[0]
        self.line = line_no.group(1).strip()
        self.column = column_no.group(1).strip()
