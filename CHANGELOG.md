**BREAKING RELEASE**

ansible-later contains some fundamental restructuring and is not backward compatible
with old releases. 

- BREAKING
  - Switch configuration files to YAML
  - Enable multi location configuration files [#14](https://github.com/xoxys/ansible-later/issues/14)
  - ID's used in standards have to be unique (or not set)
  - `ansible_review_min_version` was renamed to `ansible_later_min_version`

- FEATURE
  - Add optional JSON logging [#13](https://github.com/xoxys/ansible-later/issues/13)
  - Add exclude options in config files [#16](https://github.com/xoxys/ansible-later/issues/16) 
  - Add multiprocessing for better perfomance [#12](https://github.com/xoxys/ansible-later/issues/12)

- ENHANCEMENT
  - Allow passing glob patterns to cli [#16](https://github.com/xoxys/ansible-later/issues/16)
  - Rule settings (e.g. for yamllint) can be set in config file [#7](https://github.com/xoxys/ansible-later/issues/7)
  - Remove simple print outputs and switch to python logging module [#13](https://github.com/xoxys/ansible-later/issues/13)
  - Restructure log output for better readability [#13](https://github.com/xoxys/ansible-later/issues/13)
  - Better loglevel control from cli (-vvv/-qqq) [#13](https://github.com/xoxys/ansible-later/issues/13)
  - Better inventory file classification [#15](https://github.com/xoxys/ansible-later/issues/15)
