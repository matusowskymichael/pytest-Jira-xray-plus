"""Early marker validation with synthetic values and forbidden upload transport."""

import json
import os

import pytest


def prepare(pytester, monkeypatch, expression, include_valid_first=False):
    for key in list(os.environ):
        if key.startswith(('XRAY_', 'PYTEST_')):
            monkeypatch.delenv(key)
    for key, value in {
        'XRAY_API_BASE_URL': 'https://example.invalid',
        'XRAY_API_USER': 'synthetic',
        'XRAY_API_PASSWORD': 'synthetic',
    }.items():
        monkeypatch.setenv(key, value)
    pytester.makeconftest("""
        from pathlib import Path
        import pytest
        import requests
        from pytest_xray.xray_publisher import XrayPublisher
        def forbidden(*args, **kwargs):
            Path('upload-attempted').touch()
            raise AssertionError('transport forbidden')
        XrayPublisher.publish = forbidden
        requests.sessions.Session.request = forbidden
        @pytest.fixture(autouse=True)
        def execution_probe():
            Path('fixture-executed').touch()
    """)
    if include_valid_first:
        pytester.makepyfile(test_a_valid="import pytest\n@pytest.mark.xray('SYN-2')\ndef test_a_valid(): pass\n")
    pytester.makepyfile(f"""
        import pytest
        class Secret:
            def __repr__(self):
                raise AssertionError('secret repr invoked')
        @pytest.mark.xray('SYN-1', defects={expression})
        def test_case(): pass
    """)


@pytest.mark.parametrize(
    'expression',
    [
        "'sensitive-marker-value'",
        'None',
        "('sensitive-marker-value',)",
        "{'sensitive-marker-value': 'value'}",
        '17',
        '[17]',
        "['']",
        "['  ']",
        '[Secret()]',
    ],
)
@pytest.mark.parametrize('upload', [False, True])
def test_invalid_defects_stop_before_fixtures_and_upload(pytester, monkeypatch, expression, upload):
    prepare(pytester, monkeypatch, expression, include_valid_first=True)
    args = ['--jira-xray', '--continue-on-collection-errors']
    if not upload:
        args.append('--xraypath=xray.json')
    result = pytester.runpytest_subprocess(*args)
    assert result.ret != 0
    output = result.stdout.str() + result.stderr.str()
    assert 'defects must be a list of nonempty strings' in output
    assert 'sensitive-marker-value' not in output
    assert 'secret repr invoked' not in output
    assert 'INTERNALERROR' not in output
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()


@pytest.mark.parametrize('expression', ["'sensitive-marker-value'", '[Secret()]'])
@pytest.mark.parametrize('upload', [False, True])
def test_invalid_defects_stop_xdist_workers(pytester, monkeypatch, expression, upload):
    prepare(pytester, monkeypatch, expression, include_valid_first=True)
    args = ['--jira-xray', '-n', '2', '--max-worker-restart=0', '--continue-on-collection-errors']
    if not upload:
        args.append('--xraypath=xray.json')
    result = pytester.runpytest_subprocess(*args)
    assert result.ret != 0
    output = result.stdout.str() + result.stderr.str()
    assert 'defects must be a list of nonempty strings' in output
    assert 'sensitive-marker-value' not in output
    assert 'secret repr invoked' not in output
    assert 'INTERNALERROR' not in output
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('values', [[], ['BUG-1'], ['custom key', ' odd ', 'BUG-1', 'BUG-1']])
def test_valid_defects_are_preserved_without_key_format_rules(pytester, monkeypatch, workers, values):
    prepare(pytester, monkeypatch, repr(values))
    result = pytester.runpytest_subprocess('--jira-xray', '--xraypath=xray.json', '-n', str(workers))
    result.assert_outcomes(passed=1)
    test = json.loads((pytester.path / 'xray.json').read_text())['tests'][0]
    assert test.get('defects', []) == values
    assert test['status'] == 'PASS'
    assert (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()


@pytest.mark.parametrize('case_report', [False, True])
def test_reporting_disabled_does_not_validate_defects(pytester, monkeypatch, case_report):
    prepare(pytester, monkeypatch, "'sensitive-marker-value'")
    result = pytester.runpytest_subprocess(*(['--xray-case-report=cases.json'] if case_report else []))
    result.assert_outcomes(passed=1)
    assert (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()


def test_collect_only_retains_disabled_reporting_behavior(pytester, monkeypatch):
    prepare(pytester, monkeypatch, "['']", include_valid_first=True)
    result = pytester.runpytest_subprocess('--jira-xray', '--xraypath=xray.json', '--collect-only')
    assert result.ret == 0
    assert 'defects must be a list of nonempty strings' not in result.stdout.str() + result.stderr.str()
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()
