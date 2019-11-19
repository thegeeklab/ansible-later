* BREAKING
  * drop support for python 2.7
* FEATURE
  * add new rule to check if yaml document end marker is present (check_yaml_document_end)
* BUGFIX
  * fix exception while tasks `name` attribute is empty
* INTERNAL
  * test only with ansible version `latest` and `devel`
  * build and release multi-arch docker images
