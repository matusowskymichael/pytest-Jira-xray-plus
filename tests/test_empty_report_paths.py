"""Explicit empty output arguments must not silently select upload or omit files."""

import json
import os

import pytest

OPTIONS = ['--xray-case-report', '--xraypath', '--xray-full-report']
SENTINELS = ['collected', 'fixture-ran', 'workers-started', 'transport-attempted']


@pytest.fixture
def suite(pytester, monkeypatch):
    for key in os.environ:
        if key.startswith('XRAY_'):
            monkeypatch.delenv(key)
    monkeypatch.setenv('XRAY_API_BASE_URL', 'https://synthetic.invalid')
    monkeypatch.setenv('XRAY_API_USER', 'synthetic')
    monkeypatch.setenv('XRAY_API_PASSWORD', 'synthetic')
    pytester.makeconftest('''
        from pathlib import Path
        import pytest
        import requests

        def fake_transport(*args, **kwargs):
            Path('transport-attempted').touch()
            response = requests.Response()
            response.status_code = 200
            response._content = b'{"testExecIssue": {"key": "SYN-2"}}'
            return response
        requests.sessions.Session.request = fake_transport

        @pytest.hookimpl(optionalhook=True)
        def pytest_xdist_setupnodes(config, specs):
            Path('workers-started').touch()
    ''')
    pytester.makepyfile('''
        from pathlib import Path
        import pytest
        Path('collected').touch()
        @pytest.fixture
        def resource():
            Path('fixture-ran').touch()
        @pytest.mark.xray('SYN-1')
        def test_case(resource): pass
    ''')
    return pytester


def args_for(option):
    if option == '--xray-case-report':
        return []
    if option == '--xraypath':
        return ['--jira-xray']
    return ['--jira-xray', '--xraypath=preview.json']


def assert_rejected(suite, result, option):
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    output = str(result.stdout) + str(result.stderr)
    assert f'{option} requires a nonempty file path' in output
    assert 'INTERNALERROR' not in output
    assert 'Traceback' not in output
    for name in SENTINELS + ['preview.json', 'cases.json', 'full.json']:
        assert not (suite.path / name).exists(), name


@pytest.mark.parametrize('option', OPTIONS)
@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('separate_value', [False, True])
def test_empty_path_rejected_before_execution(suite, option, workers, separate_value):
    argument = [option, ''] if separate_value else [f'{option}=']
    result = suite.runpytest_subprocess(*args_for(option), *argument, '-n', str(workers))
    assert_rejected(suite, result, option)


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('option, extra', [
    ('--xray-case-report', ['--jira-xray']),
    ('--xray-case-report', ['--xray-case-values']),
    ('--xray-case-report', ['--xray-case-redact-identities']),
    ('--xraypath', ['--xray-case-report=cases.json', '--xray-full-report=full.json']),
    ('--xray-full-report', ['--xray-case-report=cases.json']),
])
def test_empty_path_not_hidden_by_other_options(suite, option, extra, workers):
    result = suite.runpytest_subprocess(*args_for(option), *extra, f'{option}=', '-n', str(workers))
    assert_rejected(suite, result, option)


@pytest.mark.parametrize('workers', [0, 2])
def test_empty_export_rejected_before_authentication(suite, monkeypatch, workers):
    monkeypatch.delenv('XRAY_API_BASE_URL')
    result = suite.runpytest_subprocess('--jira-xray', '--xraypath=', '-n', str(workers))
    assert_rejected(suite, result, '--xraypath')
    assert 'requires environment variable' not in str(result.stderr)


@pytest.mark.parametrize('option', OPTIONS)
@pytest.mark.parametrize('workers', [0, 2])
def test_nonempty_filename_with_spaces_still_exports(suite, option, workers):
    result = suite.runpytest_subprocess(*args_for(option), f'{option}= report .json', '-n', str(workers))
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK
    data = json.loads((suite.path / ' report .json').read_text())
    if option == '--xray-case-report':
        assert data['cases'][0]['status'] == 'passed'
    else:
        assert data['tests'][0]['status'] == 'PASS'
    assert not (suite.path / 'transport-attempted').exists()


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('upload', [False, True])
def test_omitted_paths_preserve_default_and_upload_modes(suite, workers, upload):
    args = ['--jira-xray'] if upload else []
    result = suite.runpytest_subprocess(*args, '-n', str(workers))
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK
    assert (suite.path / 'fixture-ran').exists()
    assert (suite.path / 'transport-attempted').exists() is upload
    assert not list(suite.path.glob('*.json'))


@pytest.mark.parametrize('option', OPTIONS)
def test_collect_only_keeps_existing_bypass(suite, option):
    result = suite.runpytest_subprocess('--collect-only', *args_for(option), f'{option}=')
    assert result.ret == pytest.ExitCode.OK
    assert (suite.path / 'collected').exists()
    for name in ('fixture-ran', 'workers-started', 'transport-attempted', 'preview.json'):
        assert not (suite.path / name).exists()
