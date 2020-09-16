- DEPRECATE
  - the tag 'skip_ansible_lint' to skip tasks is deprecated
    use 'skip_ansible_later' instead
- ENHANCEMENT
  - add a non-enforcement rule for deprecated features
    if you use a custom standards file you may have to enable `check_deprecate`
- BUGFIX
  - ANSIBLE0010 - allow `shell` module if `args.executable` is used
    as this parameter is no longer support by command module
