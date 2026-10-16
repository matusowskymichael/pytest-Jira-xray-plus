"""Synthetic list-ownership regressions; exported files only, HTTP forbidden."""

import json
import os

import pytest

from pytest_xray import evidence
from pytest_xray.helper import Status, TestCase


def test_merge_owns_report_lists_without_deduplicating_attachments():
    attachments = [evidence.text('shared', 'case.txt')]
    defects = ['BUG-1']
    first = TestCase('SYN-1', Status.PASS, 'first', evidences=attachments, defects=defects)
    sibling = TestCase('SYN-2', Status.PASS, 'first', evidences=attachments, defects=defects)
    second_attachments = [evidence.text('shared', 'case.txt')]
    second_defects = ['BUG-1', 'BUG-2']
    first.merge(TestCase('SYN-1', Status.FAIL, 'second', evidences=second_attachments, defects=second_defects))
    assert len(first.evidences) == 2  # Equal attachment content remains two occurrences.
    assert first.defects == ['BUG-1', 'BUG-2']
    assert sibling.evidences == attachments == second_attachments
    assert len(attachments) == 1
    assert sibling.defects == defects == ['BUG-1']
    assert second_defects == ['BUG-1', 'BUG-2']
    assert first.status == Status.FAIL and sibling.status == Status.PASS
    assert first.comment == 'first\n' + '-' * 80 + '\nsecond'
    assert sibling.comment == 'first'
    attachments.append(evidence.text('later', 'later.txt'))
    defects.append('BUG-3')
    assert len(sibling.evidences) == 1
    assert sibling.defects == ['BUG-1']


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('both_keys', [False, True])
@pytest.mark.parametrize('reverse', [False, True])
def test_multi_key_reports_keep_case_attachments_and_defects_isolated(
    pytester, monkeypatch, workers, both_keys, reverse
):
    for key in list(os.environ):
        if key.startswith(('XRAY_', 'PYTEST_')):
            monkeypatch.delenv(key)
    second_keys = ['SYN-1', 'SYN-2'] if both_keys else ['SYN-1']
    params = [
        "pytest.param('first', marks=pytest.mark.xray(['SYN-1', 'SYN-2'], defects=['BUG-1']))",
        f"pytest.param('second', marks=pytest.mark.xray({second_keys!r}, defects=['BUG-2']))",
    ]
    if reverse:
        params.reverse()
    pytester.makeconftest(f"""
        import pytest
        import requests
        from pytest_xray import evidence
        def blocked(*args, **kwargs):
            raise AssertionError('HTTP forbidden in attachment ownership regression')
        requests.sessions.Session.request = blocked
        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtest_makereport(item, call):
            outcome = yield
            report = outcome.get_result()
            if report.when == 'call':
                value = 'identical' if {both_keys!r} else item.callspec.params['value']
                report.evidences = [evidence.text(value, 'case.txt')]
    """)
    pytester.makepyfile(f"""
        import pytest
        @pytest.mark.parametrize('value', [{', '.join(params)}])
        def test_case(value):
            assert value == 'first', 'synthetic second-case failure'
    """)
    result = pytester.runpytest_subprocess(
        '-q',
        '-n',
        str(workers),
        '--jira-xray',
        '--xraypath=xray.json',
        '--allow-duplicate-ids',
        '--xray-parameter-details',
    )
    result.assert_outcomes(passed=1, failed=1)
    tests = {t['testKey']: t for t in json.loads((pytester.path / 'xray.json').read_text())['tests']}
    assert set(tests) == {'SYN-1', 'SYN-2'}
    for key, test in tests.items():
        values = ['first', 'second'] if key == 'SYN-1' or both_keys else ['first']
        expected = [evidence.text('identical' if both_keys else value, 'case.txt') for value in values]
        assert sorted(test['evidences'], key=lambda item: item['data']) == sorted(
            expected, key=lambda item: item['data']
        )
        assert set(test['defects']) == ({'BUG-1', 'BUG-2'} if len(values) == 2 else {'BUG-1'})
        assert test['status'] == ('FAIL' if len(values) == 2 else 'PASS')
        entries = [
            json.loads(line.split('pytest parameter case: ', 1)[1])
            for line in test['comment'].splitlines()
            if 'pytest parameter case: ' in line
        ]
        assert sorted(entry['parameters']['value'] for entry in entries) == values
