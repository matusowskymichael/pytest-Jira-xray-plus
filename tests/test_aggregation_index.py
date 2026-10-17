"""Result-stream scaling and payload preservation; synthetic reports only."""

import json
from types import SimpleNamespace

import pytest

from pytest_xray import evidence
from pytest_xray.helper import STATUS_STR_MAPPER_CLOUD, STATUS_STR_MAPPER_JIRA, Status, TestCase, TestExecution
from pytest_xray.xray_plugin import XrayPlugin


def plugin(cloud=False):
    config = SimpleNamespace(getoption=lambda name, default=None: cloud if name == '--cloud' else default)
    return XrayPlugin(config, None)


def report(keys, outcome='passed', phase='call', comment='', defects=None, attachments=None, xfail=False):
    result = SimpleNamespace(
        nodeid='synthetic', test_keys={'synthetic': keys}, outcome=outcome,
        passed=outcome == 'passed', failed=outcome == 'failed', skipped=outcome == 'skipped',
        when=phase, longrepr=comment, longreprtext=comment,
        defects={'synthetic': defects or []}, evidences=attachments or [],
    )
    if xfail:
        result.wasxfail = 'synthetic expected failure'
    return result


class CountedKey(str):
    comparisons = 0

    def __hash__(self):
        return int(self.split('-')[1])

    def __eq__(self, other):
        type(self).comparisons += 1
        return super().__eq__(other)


@pytest.mark.parametrize('size', [128, 256, 512])
@pytest.mark.parametrize('rounds', [1, 3])
def test_result_key_comparison_work_is_bounded(size, rounds):
    instance = plugin()
    CountedKey.comparisons = 0
    for _ in range(rounds):
        for number in range(size):
            instance.pytest_runtest_logreport(report([CountedKey(f'SYN-{number}')]))
    comparisons = CountedKey.comparisons
    assert comparisons <= size * rounds * 4
    assert len(instance.test_execution.tests) == size
    assert [str(t.test_key) for t in instance.test_execution.tests] == [f'SYN-{n}' for n in range(size)]
    assert all(t.status == Status.PASS for t in instance.test_execution.tests)


@pytest.mark.parametrize('cloud', [False, True])
@pytest.mark.parametrize('reverse', [False, True])
def test_stream_preserves_order_status_comments_defects_and_evidence(cloud, reverse):
    instance = plugin(cloud)
    mapper = STATUS_STR_MAPPER_CLOUD if cloud else STATUS_STR_MAPPER_JIRA
    rows = [
        (['SYN-2', 'SYN-1'], 'passed', 'call', 'first', ['BUG-1'], Status.PASS, False),
        (['SYN-2'], 'skipped', 'setup', 'skip', ['BUG-1', 'BUG-2'], Status.ABORTED, False),
        (['SYN-3'], 'rerun', 'call', 'retry', [], Status.FAIL, False),
        (['SYN-3'], 'passed', 'call', 'last', [], Status.PASS, False),
        (['SYN-1'], 'failed', 'teardown', 'cleanup', ['BUG-2'], Status.FAIL, False),
        (['SYN-4'], 'skipped', 'call', 'xfail', [], Status.FAIL, True),
        (['SYN-5'], 'passed', 'call', 'xpass', [], Status.PASS, True),
    ]
    if reverse:
        rows.reverse()
    expected = []
    for keys, outcome, phase, comment, defects, status, xfail in rows:
        attachments = [evidence.text('identical attachment', 'case.txt')]
        instance.pytest_runtest_logreport(report(keys, outcome, phase, comment, defects, attachments, xfail))
        for key in keys:
            observation = TestCase(key, status, comment, mapper, attachments, defects)
            previous = next((t for t in expected if t.test_key == key), None)
            if previous is None:
                expected.append(observation)
            else:
                previous.merge(observation)
    instance.pytest_runtest_logreport(report(['IGNORED'], phase='setup'))
    instance.pytest_runtest_logreport(report(['IGNORED'], phase='teardown'))
    instance.pytest_runtest_logreport(report([], outcome='failed'))
    assert instance.test_execution.as_dict()['tests'] == [t.as_dict() for t in expected]
    assert len(instance.test_execution.tests) == 5


def test_public_execution_model_keeps_mutable_list_lookup_semantics():
    first = TestCase('SYN-1', Status.PASS)
    second = TestCase('SYN-1', Status.FAIL)
    execution = TestExecution(tests=[first, second])
    assert execution.find_test_case('SYN-1') is first
    execution.tests.reverse()
    assert execution.find_test_case('SYN-1') is second
    second.test_key = 'SYN-2'
    assert execution.find_test_case('SYN-1') is first
    execution.tests = [second]
    with pytest.raises(KeyError):
        execution.find_test_case('SYN-1')
    execution.append({'test_key': 'SYN-3', 'status': Status.PASS})
    assert execution.find_test_case('SYN-3') is execution.tests[-1]


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('cloud', [False, True])
def test_grouped_reruns_and_final_payload_hook(pytester, workers, cloud):
    pytester.makeconftest('''
        import pytest
        import requests
        from pytest_xray import evidence
        def blocked(*args, **kwargs):
            raise AssertionError('HTTP forbidden')
        requests.sessions.Session.request = blocked
        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtest_makereport(item, call):
            outcome = yield
            result = outcome.get_result()
            if result.when == 'call':
                result.evidences = [evidence.text(item.callspec.id, 'case.txt')]
        def pytest_xray_results(results):
            results['info']['revision'] = 'synthetic-hook'
            results['tests'].reverse()
            results['tests'][0]['comment'] += '\\nfinal-hook'
    ''')
    pytester.makepyfile('''
        import pytest
        seen = set()
        @pytest.mark.parametrize('value', [
            pytest.param('retry', marks=pytest.mark.xray('SYN-2', 'SYN-1', defects=['BUG-1'])),
            pytest.param('pass', marks=pytest.mark.xray('SYN-1', defects=['BUG-2'])),
        ])
        def test_case(value):
            if value == 'retry' and value not in seen:
                seen.add(value)
                assert False, 'synthetic retry'
    ''')
    args = ['-q', '-n', str(workers), '--reruns=1', '--jira-xray', '--xraypath=preview.json',
            '--allow-duplicate-ids', '--xray-parameter-details', '--xray-case-report=cases.json']
    if cloud:
        args.append('--cloud')
    result = pytester.runpytest_subprocess(*args)
    result.assert_outcomes(passed=2)
    assert result.ret == pytest.ExitCode.OK
    result.stdout.fnmatch_lines(['*2 passed, 1 rerun*'])
    payload = json.loads((pytester.path / 'preview.json').read_text())
    assert payload['info']['revision'] == 'synthetic-hook'
    assert payload['tests'][0]['comment'].endswith('final-hook')
    tests = {t['testKey']: t for t in payload['tests']}
    assert set(tests) == {'SYN-1', 'SYN-2'}
    for key, test in tests.items():
        assert test['status'] == ('FAILED' if cloud else 'FAIL')
        assert len(test['evidences']) == (3 if key == 'SYN-1' else 2)
        assert set(test['defects']) == ({'BUG-1', 'BUG-2'} if key == 'SYN-1' else {'BUG-1'})
        assert test['comment'].count('pytest parameter case:') == (3 if key == 'SYN-1' else 2)
        assert 'iterations' not in test
    cases = json.loads((pytester.path / 'cases.json').read_text())['cases']
    assert sorted(c['status'] for c in cases) == ['failed', 'passed']
    assert sorted(len(c['attempts']) for c in cases) == [1, 2]
