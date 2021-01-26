from ansible.parsing.yaml.objects import AnsibleMapping

from ansiblelater.standard import StandardBase


class CheckScmInSrc(StandardBase):

    sid = "ANSIBLE0005"
    description = "Use `scm:` key rather than `src: scm+url`"
    helptext = "usage of `src: scm+url` not recommended"
    version = "0.1"
    types = ["rolesfile"]

    def check(self, candidate, settings):
        roles, errors = self.get_tasks(candidate, settings)

        if not errors:
            for role in roles:
                if isinstance(role, AnsibleMapping):
                    if "+" in role.get("src"):
                        errors.append(self.Error(role["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
