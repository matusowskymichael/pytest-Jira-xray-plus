"""Malformed Test keys are configuration errors, never worker/internal crashes."""

import json
import os

import pytest


def prepare(pytester, monkeypatch, arguments):
    for name in list(os.environ):
        if name.startswith(('XRAY_', 'PYTEST_')):
            monkeypatch.delenv(name)
    monkeypatch.setenv('XRAY_API_BASE_URL', 'https://example.invalid')
    monkeypatch.setenv('XRAY_API_USER', 'synthetic')
    monkeypatch.setenv('XRAY_API_PASSWORD', 'synthetic')
    pytester.makeconftest('''
from pathlib import Path
import pytest
import requests
import os
from pytest_xray.xray_publisher import XrayPublisher
def forbidden(*args, **kwargs):
    Path('upload-attempted').touch()
    raise AssertionError('transport forbidden')
def pytest_deselected(items):
    Path(f'deselected-{os.getpid()}').write_text(str(len(items)))
XrayPublisher.publish = forbidden
requests.sessions.Session.request = forbidden
@pytest.fixture(autouse=True)
def execution_probe():
    Path('fixture-executed').touch()
''')
    pytester.makepyfile(test_a_valid="import pytest\n@pytest.mark.xray('SYN-2')\ndef test_a_valid(): pass")
    pytester.makepyfile(test_z_invalid=f'''
import pytest
class Secret:
    def __repr__(self):
        raise AssertionError('secret repr invoked')
@pytest.mark.xray({arguments})
def test_invalid(): pass
''')


@pytest.mark.parametrize('arguments', ['', "''", "'   '", '[]', 'None', '17', '[Secret()]', "'SYN-1', 17"])
@pytest.mark.parametrize('upload', [False, True])
def test_malformed_keys_fail_collection_without_execution_or_upload(pytester, monkeypatch, arguments, upload):
    prepare(pytester, monkeypatch, arguments)
    args = ['--jira-xray', '--continue-on-collection-errors']
    if not upload:
        args += ['--xraypath=xray.json']
    result = pytester.runpytest_subprocess(*args)
    assert result.ret != 0
    output = result.stdout.str() + result.stderr.str()
    assert 'xray marker configuration' in output
    notifications = list(pytester.path.glob('deselected-*'))
    assert notifications and all(p.read_text() == '2' for p in notifications)
    assert 'INTERNALERROR' not in output
    assert 'secret repr invoked' not in output
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()
    if not upload:
        assert json.loads((pytester.path / 'xray.json').read_text())['tests'] == []


@pytest.mark.parametrize('arguments', ['', '[Secret()]'])
@pytest.mark.parametrize('upload', [False, True])
def test_malformed_keys_stop_xdist_without_worker_crash(pytester, monkeypatch, arguments, upload):
    prepare(pytester, monkeypatch, arguments)
    args = ['--jira-xray', '-n', '2', '--max-worker-restart=0', '--continue-on-collection-errors']
    if not upload:
        args += ['--xraypath=xray.json']
    result = pytester.runpytest_subprocess(*args)
    output = result.stdout.str() + result.stderr.str()
    assert result.ret != 0
    assert 'xray marker configuration' in output
    notifications = list(pytester.path.glob('deselected-*'))
    assert notifications and all(p.read_text() == '2' for p in notifications)
    assert 'INTERNALERROR' not in output
    assert 'replacing crashed worker' not in output
    assert 'Not properly terminated' not in output
    assert 'secret repr invoked' not in output
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()


@pytest.mark.parametrize('args', [[], ['--xray-case-report=cases.json']])
def test_disabled_xray_does_not_validate_keys(pytester, monkeypatch, args):
    prepare(pytester, monkeypatch, '')
    pytester.runpytest_subprocess(*args).assert_outcomes(passed=2)
    assert (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()


def test_collect_only_still_lists_malformed_keys_without_execution(pytester, monkeypatch):
    prepare(pytester, monkeypatch, '')
    result = pytester.runpytest_subprocess('--collect-only', '--jira-xray', '--xraypath=xray.json')
    assert result.ret == 0
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()


@pytest.mark.parametrize('arguments', ["' odd ', 'custom key', ' odd '", "[' odd ', 'custom key', ' odd ']"])
@pytest.mark.parametrize('workers', [0, 2])
def test_valid_key_forms_order_and_deduplication_are_preserved(pytester, monkeypatch, arguments, workers):
    prepare(pytester, monkeypatch, arguments)
    result = pytester.runpytest_subprocess('--jira-xray', '--xraypath=xray.json', '-n', str(workers))
    result.assert_outcomes(passed=2)
    data = json.loads((pytester.path / 'xray.json').read_text())['tests']
    # xdist completion order can differ across items; marker order stays stable.
    keys = [row['testKey'] for row in data]
    assert set(keys) == {'SYN-2', ' odd ', 'custom key'}
    assert keys.index(' odd ') < keys.index('custom key')
    assert len(keys) == 3
    assert not (pytester.path / 'upload-attempted').exists()
