# ansible-later

Another best practice scanner for Ansible roles and playbooks

[![Build Status](https://img.shields.io/drone/build/thegeeklab/ansible-later?logo=drone&server=https%3A%2F%2Fdrone.thegeeklab.de)](https://drone.thegeeklab.de/thegeeklab/ansible-later)
[![Docker Hub](https://img.shields.io/badge/dockerhub-latest-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/thegeeklab/ansible-later)
[![Quay.io](https://img.shields.io/badge/quay-latest-blue.svg?logo=docker&logoColor=white)](https://quay.io/repository/thegeeklab/ansible-later)
[![Python Version](https://img.shields.io/pypi/pyversions/ansible-later.svg)](https://pypi.org/project/ansible-later/)
[![PyPI Status](https://img.shields.io/pypi/status/ansible-later.svg)](https://pypi.org/project/ansible-later/)
[![PyPI Release](https://img.shields.io/pypi/v/ansible-later.svg)](https://pypi.org/project/ansible-later/)
[![Codecov](https://img.shields.io/codecov/c/github/thegeeklab/ansible-later)](https://codecov.io/gh/thegeeklab/ansible-later)
[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/ansible-later)](https://github.com/thegeeklab/ansible-later/graphs/contributors)
[![Source: GitHub](https://img.shields.io/badge/source-github-blue.svg?logo=github&logoColor=white)](https://github.com/thegeeklab/ansible-later)
[![License: MIT](https://img.shields.io/github/license/thegeeklab/ansible-later)](https://github.com/thegeeklab/ansible-later/blob/main/LICENSE)

ansible-later is a best practice scanner and linting tool. In most cases, if you write Ansible roles in a team, it helps to have a coding or best practice guideline in place. This will make Ansible roles more readable for all maintainers and can reduce the troubleshooting time. While ansible-later aims to be a fast and easy to use linting tool for your Ansible resources, it might not be that feature completed as required in some situations. If you need a more in-depth analysis you can take a look at [ansible-lint](https://github.com/ansible-community/ansible-lint).

ansible-later does **not** ensure that your role will work as expected. For deployment tests you can use other tools like [molecule](https://github.com/ansible/molecule).

You can find the full documentation at [https://ansible-later.geekdocs.de](https://ansible-later.geekdocs.de/).

## Community

<!-- prettier-ignore-start -->
<!-- spellchecker-disable -->

- [GitHub Action](https://github.com/patrickjahns/ansible-later-action) by [@patrickjahns](https://github.com/patrickjahns)

<!-- spellchecker-enable -->
<!-- prettier-ignore-end -->

## Contributors

Special thanks goes to all [contributors](https://github.com/thegeeklab/ansible-later/graphs/contributors). If you would like to contribute,
please see the [instructions](https://github.com/thegeeklab/ansible-later/blob/main/CONTRIBUTING.md).

ansible-later is a fork of Will Thames [ansible-review](https://github.com/willthames/ansible-review). Thanks for your work on ansible-review and ansible-lint.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/thegeeklab/ansible-later/blob/main/LICENSE) file for details.
