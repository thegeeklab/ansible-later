"""Review candidates."""

from six import iteritems


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
