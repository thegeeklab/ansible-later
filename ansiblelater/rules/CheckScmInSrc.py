from ansible.parsing.yaml.objects import AnsibleMapping

from ansiblelater.rule import RuleBase


class CheckScmInSrc(RuleBase):
    rid = "ANS105"
    description = "Use `scm:` key rather than `src: scm+url`"
    helptext = "usage of `src: scm+url` not recommended"
    types = ["rolesfile"]

    def check(self, candidate, settings):
        roles, errors = self.get_tasks(candidate, settings)

        if not errors:
            for role in roles:
                if (
                    isinstance(role, AnsibleMapping)
                    and bool(role.get("src"))
                    and "+" in role.get("src")
                ):
                    errors.append(self.Error(role["__line__"], self.helptext))

        return self.Result(candidate.path, errors)
