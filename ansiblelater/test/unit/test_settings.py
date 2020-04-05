"""Test settings module."""

import pytest

from ansiblelater import settings


@pytest.fixture
def settings_instance():
    c = settings.Settings(args={"rules": {"files": []}})

    return c


def test_args_member(settings_instance):
    x = {"rules": {"files": ["*"]}}

    assert x == settings_instance.args


def test_args_setter(settings_instance):
    default = {"rules.files": ["dummy"], "config_file": "conf.yml"}
    x = {"rules": {"files": ["dummy"]}}

    s = settings_instance._set_args(default)

    assert x == s
