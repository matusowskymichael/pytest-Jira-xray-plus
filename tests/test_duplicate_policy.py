"""Disallowed duplicate keys are collection failures, not plugin crashes."""

import json

import pytest

from tests.test_key_validation import prepare


def duplicate_suite(pytester, monkeypatch):
    prepare(pytester, monkeypatch, "'SYN-1', 'SYN-2', 'SYN-1'")
    (pytester.path / 'test_a_valid.py').write_text(
        "import pytest\n@pytest.mark.xray('SYN-2', 'SYN-1')\ndef test_a_valid(): pass\n"
    )


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('upload', [False, True])
@pytest.mark.parametrize('continue_collection', [False, True])
def test_disallowed_duplicates_are_controlled_collection_errors(
    pytester, monkeypatch, workers, upload, continue_collection
):
    duplicate_suite(pytester, monkeypatch)
    args = ['--jira-xray', '-n', str(workers), '--max-worker-restart=0']
    if continue_collection:
        args += ['--continue-on-collection-errors']
    if not upload:
        args += ['--xraypath=preview.json']
    result = pytester.runpytest_subprocess(*args)
    output = result.stdout.str() + result.stderr.str()
    assert result.ret in (pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.INTERRUPTED)
    assert "Duplicated test case ids: ['SYN-1', 'SYN-2']" in output
    assert 'INTERNALERROR' not in output
    assert 'Not properly terminated' not in output
    assert 'replacing crashed worker' not in output
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()
    notifications = list(pytester.path.glob('deselected-*'))
    assert notifications and all(path.read_text() == '2' for path in notifications)
    if not upload:
        assert json.loads((pytester.path / 'preview.json').read_text())['tests'] == []


@pytest.mark.parametrize('workers', [0, 2])
def test_allow_duplicates_retains_grouping(pytester, monkeypatch, workers):
    duplicate_suite(pytester, monkeypatch)
    result = pytester.runpytest_subprocess(
        '--jira-xray', '--allow-duplicate-ids', '--xraypath=preview.json', '-n', str(workers)
    )
    result.assert_outcomes(passed=2)
    tests = json.loads((pytester.path / 'preview.json').read_text())['tests']
    assert {(test['testKey'], test['status']) for test in tests} == {('SYN-1', 'PASS'), ('SYN-2', 'PASS')}
    assert len(tests) == 2
    assert not (pytester.path / 'upload-attempted').exists()


@pytest.mark.parametrize('args', [[], ['--xray-case-report=cases.json']])
def test_disabled_xray_does_not_apply_duplicate_policy(pytester, monkeypatch, args):
    duplicate_suite(pytester, monkeypatch)
    pytester.runpytest_subprocess(*args).assert_outcomes(passed=2)
    assert not (pytester.path / 'upload-attempted').exists()


def test_collect_only_does_not_apply_duplicate_policy(pytester, monkeypatch):
    duplicate_suite(pytester, monkeypatch)
    result = pytester.runpytest_subprocess('--collect-only', '--jira-xray', '--xraypath=preview.json')
    assert result.ret == 0
    assert not (pytester.path / 'fixture-executed').exists()
    assert not (pytester.path / 'upload-attempted').exists()
