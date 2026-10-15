"""Pure-model edge cases that do not need pytest report objects."""

from pytest_xray.case_results import CaseResults, PhaseResult


def test_incomplete_attempt_is_preserved_when_another_attempt_starts():
    results = CaseResults()
    for phase in ['setup', 'call', 'setup', 'call', 'teardown']:
        results.record('test.py::test_case[value]', 'local', 'value', PhaseResult(phase, 'passed', 'passed', 0))
    case = results.as_dict(0)['cases'][0]
    assert case['status'] == 'incomplete'
    assert [a['status'] for a in case['attempts']] == ['incomplete', 'passed']
    assert [len(a['phases']) for a in case['attempts']] == [2, 3]


def test_skip_cannot_hide_a_failed_attempt():
    results = CaseResults()
    for outcome in ['failed', 'skipped', 'passed']:
        for phase in ['setup', 'call', 'teardown']:
            value = outcome if phase == 'call' else 'passed'
            results.record('test.py::test_case', 'local', None, PhaseResult(phase, value, value, 0))
    case = results.as_dict(0)['cases'][0]
    assert case['status'] == 'failed'
    assert len(case['attempts']) == 3
