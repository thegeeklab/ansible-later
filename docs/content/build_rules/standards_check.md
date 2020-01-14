---
title: Minimal standards checks
---

A typical standards check will look like:

{{< highlight Python "linenos=table" >}}
def check_playbook_for_something(candidate, settings):
    result = Result(candidate.path) # empty result is a success with no output
    with open(candidate.path, 'r') as f:
        for (lineno, line) in enumerate(f):
            if line is dodgy:
                # enumerate is 0-based so add 1 to lineno
                result.errors.append(Error(lineno+1, "Line is dodgy: reasons"))
    return result
{{< /highlight >}}

All standards check take a candidate object, which has a path attribute.
The type can be inferred from the class name (i.e. `type(candidate).__name__`)
or from the table [here](#candidates).

They return a `Result` object, which contains a possibly empty list of `Error`
objects. `Error` objects are formed of a line number and a message. If the
error applies to the whole file being reviewed, set the line number to `None`.
Line numbers are important as `ansible-later` can review just ranges of files
to only review changes (e.g. through piping the output of `git diff` to
`ansible-later`).
