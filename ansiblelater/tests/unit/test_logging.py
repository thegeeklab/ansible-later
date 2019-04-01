from __future__ import print_function

import colorama
import logging

from ansiblelater.utils import info, warn, abort, error, should_do_markup


def test_abort(capsys, mocker):
    abort('foo')
    stdout, _ = capsys.readouterr()

    print('{}{}{}'.format(colorama.Fore.RED, 'FATAL: foo'.rstrip(),
                          colorama.Style.RESET_ALL))
    x, _ = capsys.readouterr()

    assert x == stdout


def test_error(capsys, mocker):
    error('foo')
    stdout, _ = capsys.readouterr()

    print('{}{}{}'.format(colorama.Fore.RED, 'ERROR: foo'.rstrip(),
                          colorama.Style.RESET_ALL))
    x, _ = capsys.readouterr()

    assert x == stdout


def test_warn(capsys, mocker):
    settings = mocker.MagicMock()
    settings.log_level = getattr(logging, 'WARNING')

    warn('foo', settings)
    stdout, _ = capsys.readouterr()

    print('{}{}{}'.format(colorama.Fore.YELLOW, 'WARN: foo'.rstrip(),
                          colorama.Style.RESET_ALL))
    x, _ = capsys.readouterr()

    assert x == stdout


def test_info(capsys, mocker):
    settings = mocker.MagicMock()
    settings.log_level = getattr(logging, 'INFO')

    info('foo', settings)
    stdout, _ = capsys.readouterr()

    print('{}{}{}'.format(colorama.Fore.BLUE, 'INFO: foo'.rstrip(),
                          colorama.Style.RESET_ALL))
    x, _ = capsys.readouterr()

    assert x == stdout


def test_markup_detection_pycolors0(monkeypatch):
    monkeypatch.setenv('PY_COLORS', '0')
    assert not should_do_markup()


def test_markup_detection_pycolors1(monkeypatch):
    monkeypatch.setenv('PY_COLORS', '1')
    assert should_do_markup()


def test_markup_detection_tty_yes(mocker):
    mocker.patch('sys.stdout.isatty', return_value=True)
    mocker.patch('os.environ', {'TERM': 'xterm'})
    assert should_do_markup()
    mocker.resetall()
    mocker.stopall()


def test_markup_detection_tty_no(mocker):
    mocker.patch('os.environ', {})
    mocker.patch('sys.stdout.isatty', return_value=False)
    assert not should_do_markup()
    mocker.resetall()
    mocker.stopall()
