"""Synthetic configuration failures must stop before collection or transport."""

import os

import pytest

MODES = {'basic': [], 'token': ['--api-key-auth'], 'cloud': ['--cloud', '--client-secret-auth']}
ENVIRONMENT = {
    'XRAY_API_BASE_URL': 'https://example.invalid',
    'XRAY_API_USER': 'synthetic-user',
    'XRAY_API_PASSWORD': 'synthetic-password',
    'XRAY_API_KEY': 'synthetic-token',
    'XRAY_CLIENT_ID': 'synthetic-client',
    'XRAY_CLIENT_SECRET': 'synthetic-secret',
    'XRAY_API_VERIFY_SSL': 'True',
}
CASES = [(mode, 'XRAY_API_BASE_URL') for mode in MODES] + [
    ('basic', 'XRAY_API_USER'), ('basic', 'XRAY_API_PASSWORD'),
    ('token', 'XRAY_API_KEY'), ('cloud', 'XRAY_CLIENT_ID'), ('cloud', 'XRAY_CLIENT_SECRET'),
] + [(mode, 'missing-ca') for mode in MODES]


@pytest.fixture
def synthetic_suite(pytester, monkeypatch):
    for key in os.environ:
        if key.startswith('XRAY_'):
            monkeypatch.delenv(key)
    for key, value in ENVIRONMENT.items():
        monkeypatch.setenv(key, value)
    pytester.makeconftest('''
        from pathlib import Path
        import requests
        def blocked(*args, **kwargs):
            Path('transport-called').touch()
            raise AssertionError('network forbidden')
        requests.sessions.Session.request = blocked
    ''')
    pytester.makepyfile('''
        from pathlib import Path
        import pytest
        Path('collection-started').touch()
        @pytest.fixture
        def resource():
            Path('fixture-started').touch()
        @pytest.mark.xray('SYN-1')
        def test_case(resource): pass
    ''')
    return pytester


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('mode,missing', CASES)
def test_auth_configuration_is_usage_error(synthetic_suite, monkeypatch, mode, missing, workers):
    pytester = synthetic_suite
    if missing == 'missing-ca':
        monkeypatch.setenv('XRAY_API_VERIFY_SSL', str(pytester.path / 'missing-ca.pem'))
        diagnostic = 'Cannot find certificate file'
    else:
        monkeypatch.delenv(missing)
        diagnostic = missing
    args = ['--jira-xray', *MODES[mode], '--xray-case-report=cases.json']
    if workers:
        args += ['-n', str(workers)]
    result = pytester.runpytest_subprocess(*args)
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    output = str(result.stdout) + str(result.stderr)
    assert diagnostic in output
    assert 'ERROR:' in output
    assert 'INTERNALERROR' not in output
    assert 'Traceback' not in output
    for secret in ('synthetic-password', 'synthetic-token', 'synthetic-secret'):
        assert secret not in output
    for filename in ('collection-started', 'fixture-started', 'transport-called', 'cases.json'):
        assert not (pytester.path / filename).exists()


@pytest.mark.parametrize('args', [
    ['--jira-xray', '--xraypath=preview.json'],
    ['--xray-case-report=cases.json'],
    ['--jira-xray', '--collect-only'],
])
def test_offline_and_collection_modes_do_not_require_auth(synthetic_suite, monkeypatch, args):
    pytester = synthetic_suite
    for key in ENVIRONMENT:
        monkeypatch.delenv(key)
    result = pytester.runpytest_subprocess(*args)
    assert result.ret == pytest.ExitCode.OK
    assert not (pytester.path / 'transport-called').exists()
