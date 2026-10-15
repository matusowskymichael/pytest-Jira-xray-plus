"""Synthetic failure and installed-plugin regressions; no external services."""

import json
from unittest.mock import Mock

import pytest
import requests

from pytest_xray.exceptions import XrayError
from pytest_xray.file_publisher import FilePublisher
from pytest_xray.xray_publisher import REQUEST_TIMEOUT, ClientSecretAuth, XrayPublisher


@pytest.mark.parametrize('error', [requests.Timeout, requests.ConnectionError, requests.TooManyRedirects])
def test_transport_errors_are_normalized_without_retry(monkeypatch, error):
    send = Mock(side_effect=error('synthetic secret must not be echoed'))
    monkeypatch.setattr(requests, 'request', send)
    with pytest.raises(XrayError) as caught:
        XrayPublisher('https://example.invalid', '/import', None).publish({})
    assert 'secret' not in str(caught.value)
    assert send.call_count == 1
    assert send.call_args.kwargs['timeout'] == REQUEST_TIMEOUT
    assert send.call_args.kwargs['allow_redirects'] is False


@pytest.mark.parametrize('body', [[], None, {}, {'key': ''}, {'key': 7}, {'testExecIssue': None}])
def test_malformed_success_is_not_success(monkeypatch, body):
    response = Mock(status_code=200)
    response.json.return_value = body
    monkeypatch.setattr(requests, 'request', Mock(return_value=response))
    with pytest.raises(XrayError):
        XrayPublisher('https://example.invalid', '/import', None).publish({})


@pytest.mark.parametrize('status,body', [(401, 'secret'), (302, 'token'), (200, {}), (200, ''), (200, 'bad\ntoken')])
def test_auth_rejects_bad_response(monkeypatch, status, body):
    response = Mock(status_code=status)
    response.json.return_value = body
    if status == 401:
        response.raise_for_status.side_effect = requests.HTTPError('secret')
    post = Mock(return_value=response)
    monkeypatch.setattr(requests, 'post', post)
    request = requests.Request('POST', 'https://example.invalid').prepare()
    with pytest.raises(XrayError):
        ClientSecretAuth('https://example.invalid', 'id', 'secret')(request)
    assert 'Authorization' not in request.headers
    assert post.call_args.kwargs['timeout'] == REQUEST_TIMEOUT


def test_invalid_json_is_handled(monkeypatch):
    response = Mock(status_code=200)
    response.json.side_effect = requests.exceptions.JSONDecodeError('bad', '<html>', 0)
    monkeypatch.setattr(requests, 'request', Mock(return_value=response))
    with pytest.raises(XrayError):
        XrayPublisher('https://example.invalid', '/import', None).publish({})


def test_atomic_file_keeps_previous_report_on_serialization_failure(tmp_path):
    path = tmp_path / 'xray.json'
    path.write_text('previous')
    with pytest.raises(XrayError):
        FilePublisher(str(path)).publish({'value': object()})
    assert path.read_text() == 'previous'
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize('phase', ['setup', 'call', 'teardown'])
@pytest.mark.parametrize('workers', [0, 2])
def test_retries_agree_in_both_reports(pytester, phase, workers):
    pytester.makepyfile(f"""
        import pytest
        attempts = 0
        @pytest.fixture
        def resource():
            global attempts
            attempts += 1
            if {phase!r} == 'setup' and attempts == 1:
                pytest.fail('first setup')
            yield
            if {phase!r} == 'teardown' and attempts == 1:
                pytest.fail('first teardown')
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', [1], ids=['safe'])
        def test_retry(resource, value):
            if {phase!r} == 'call' and attempts == 1:
                pytest.fail('first call')
    """)
    result = pytester.runpytest_subprocess(
        '--reruns=1',
        '-n',
        str(workers),
        '--jira-xray',
        '--xraypath=xray.json',
        '--xray-case-report=cases.json',
        '--xray-parameter-details',
    )
    assert result.ret == 0
    case = json.loads((pytester.path / 'cases.json').read_text())['cases'][0]
    assert case['status'] == 'failed'
    assert len(case['attempts']) == 2
    xray = json.loads((pytester.path / 'xray.json').read_text())['tests'][0]
    assert xray['status'] == 'FAIL'
    assert 'rerun' in xray['comment']


@pytest.mark.parametrize(
    'source,code', [('def test_bad(: pass', 2), ('def test_interrupt(): raise KeyboardInterrupt()', 2), ('', 5)]
)
def test_partial_sessions_are_identified(pytester, source, code):
    pytester.makepyfile(source)
    result = pytester.runpytest_subprocess('--xray-case-report=cases.json')
    assert result.ret == code
    data = json.loads((pytester.path / 'cases.json').read_text())
    assert data['pytest_exit_status'] == code
    assert all(c['status'] != 'passed' for c in data['cases'])


def test_worker_crash_does_not_crash_reporter(pytester):
    pytester.makepyfile("""
        import os
        import pytest
        @pytest.mark.xray('SYN-1')
        def test_crash(): os._exit(1)
    """)
    result = pytester.runpytest_subprocess(
        '-n', '1', '--max-worker-restart=0', '--jira-xray', '--xraypath=xray.json', '--xray-case-report=cases.json'
    )
    assert result.ret == 1
    data = json.loads((pytester.path / 'cases.json').read_text())
    assert data['pytest_exit_status'] == 1
    assert any(c['status'] == 'failed' for c in data['cases'])
    assert 'INTERNALERROR' not in result.stdout.str()


def test_upload_failure_updates_local_exit_status(pytester, monkeypatch):
    monkeypatch.setenv('XRAY_API_BASE_URL', 'https://example.invalid')
    monkeypatch.setenv('XRAY_API_USER', 'synthetic')
    monkeypatch.setenv('XRAY_API_PASSWORD', 'synthetic')
    pytester.makepyfile('import pytest\n@pytest.mark.xray("SYN-1")\ndef test_ok(): pass')
    pytester.makeconftest("""
        from pytest_xray.xray_publisher import XrayPublisher
        from pytest_xray.exceptions import XrayError
        def fail(self, data): raise XrayError('synthetic upload failure')
        XrayPublisher.publish = fail
    """)
    result = pytester.runpytest_subprocess('--jira-xray', '--xray-case-report=cases.json')
    assert result.ret == 3
    assert json.loads((pytester.path / 'cases.json').read_text())['pytest_exit_status'] == 3


def test_partial_session_does_not_upload(pytester, monkeypatch):
    monkeypatch.setenv('XRAY_API_BASE_URL', 'https://example.invalid')
    monkeypatch.setenv('XRAY_API_USER', 'synthetic')
    monkeypatch.setenv('XRAY_API_PASSWORD', 'synthetic')
    pytester.makepyfile('def test_bad(: pass')
    pytester.makeconftest("""
        from pytest_xray.xray_publisher import XrayPublisher
        def forbidden(self, data): raise AssertionError('must not upload')
        XrayPublisher.publish = forbidden
    """)
    result = pytester.runpytest_subprocess('--jira-xray', '--xray-case-report=cases.json')
    assert result.ret == 2
    assert 'Upload withheld' in result.stdout.str()


@pytest.mark.parametrize('workers', [0, 2])
def test_grouped_skip_and_failure_retains_legacy_priority(pytester, workers):
    pytester.makepyfile("""
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', [0, pytest.param(1, marks=pytest.mark.skip)])
        def test_group(value): assert value
    """)
    result = pytester.runpytest_subprocess(
        '-n',
        str(workers),
        '--jira-xray',
        '--allow-duplicate-ids',
        '--xraypath=xray.json',
        '--xray-case-report=cases.json',
    )
    assert result.ret == 1
    assert json.loads((pytester.path / 'xray.json').read_text())['tests'][0]['status'] == 'ABORTED'
    assert sorted(c['status'] for c in json.loads((pytester.path / 'cases.json').read_text())['cases']) == [
        'failed',
        'skipped',
    ]


@pytest.mark.parametrize('restart', [0, 1])
def test_worker_crash_withholds_remote_import(pytester, monkeypatch, restart):
    monkeypatch.setenv('XRAY_API_BASE_URL', 'https://example.invalid')
    monkeypatch.setenv('XRAY_API_USER', 'synthetic')
    monkeypatch.setenv('XRAY_API_PASSWORD', 'synthetic')
    pytester.makepyfile("""
        import os
        import pytest
        @pytest.mark.xray('SYN-1')
        def test_a_crash(): os._exit(1)
        @pytest.mark.xray('SYN-2')
        def test_b_ok(): pass
    """)
    pytester.makeconftest("""
        from pytest_xray.xray_publisher import XrayPublisher
        def forbidden(self, data): raise AssertionError('must not upload')
        XrayPublisher.publish = forbidden
    """)
    result = pytester.runpytest_subprocess(
        '-n', '1', f'--max-worker-restart={restart}', '--jira-xray', '--xray-case-report=cases.json'
    )
    assert result.ret == 1
    assert 'Upload withheld' in result.stdout.str()
    assert 'INTERNALERROR' not in result.stdout.str()
    data = json.loads((pytester.path / 'cases.json').read_text())
    assert any(c['status'] == 'failed' for c in data['cases'])
    if restart:
        assert any(c['status'] == 'passed' for c in data['cases'])


def test_repeated_marker_key_is_not_duplicated(pytester):
    pytester.makepyfile("""
        import pytest
        @pytest.mark.xray('SYN-1', 'SYN-1')
        @pytest.mark.parametrize('value', [1])
        def test_case(value): pass
    """)
    result = pytester.runpytest_subprocess('--jira-xray', '--xraypath=xray.json', '--xray-parameter-details')
    assert result.ret == 0
    test = json.loads((pytester.path / 'xray.json').read_text())['tests'][0]
    assert test['comment'].count('pytest parameter case:') == 1


@pytest.mark.parametrize('mode', ['failfast', 'collection'])
def test_exit_one_partial_session_withholds_upload(pytester, monkeypatch, mode):
    monkeypatch.setenv('XRAY_API_BASE_URL', 'https://example.invalid')
    monkeypatch.setenv('XRAY_API_USER', 'synthetic')
    monkeypatch.setenv('XRAY_API_PASSWORD', 'synthetic')
    pytester.makeconftest("""
        from pytest_xray.xray_publisher import XrayPublisher
        def forbidden(self, data): raise AssertionError('partial upload was attempted')
        XrayPublisher.publish = forbidden
    """)
    pytester.makepyfile(
        test_cases="""
        import pytest
        @pytest.mark.xray('SYN-1')
        def test_a_fail(): assert False
        @pytest.mark.xray('SYN-2')
        def test_b_pass(): pass
    """
    )
    if mode == 'collection':
        pytester.makepyfile(test_broken='def broken(: pass')
    option = '-x' if mode == 'failfast' else '--continue-on-collection-errors'
    result = pytester.runpytest_subprocess('--jira-xray', option, '--xray-case-report=cases.json')
    assert result.ret == 1
    assert 'Upload withheld' in result.stdout.str()
    assert 'partial upload was attempted' not in result.stdout.str()
    data = json.loads((pytester.path / 'cases.json').read_text())
    assert data['pytest_exit_status'] == 1
    assert len(data['cases']) == (1 if mode == 'failfast' else 2)
