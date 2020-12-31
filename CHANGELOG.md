# Changelog

## v0.4.0 (2020-12-31)

### Fixes

- handle command module argv syntax, fixes [#47](https://github.com/thegeeklab/ansible-later/issues/47)

### Docs

- add contributing information

### Others

- **devel**: cleanup dev-dependencies
- replace master by main as default branch
- **docker**: switch to org.opencontainers image labels
- **docker**: use standalone dockerfiles for multiarch
- use renovate preset config

### Breaking Chnaged

- make ansible and ansible-base an optional extra dependency ([#53](https://github.com/thegeeklab/ansible-later/pull/53))
- drop Python 3.5 support
