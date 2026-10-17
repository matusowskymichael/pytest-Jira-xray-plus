"""Do not spend comment limits on worker headers without diagnostic content."""

import json
import os
from types import SimpleNamespace

import pytest

from pytest_xray.comment_limits import TRUNCATION_NOTICE, bound_comments
from pytest_xray.exceptions import XrayError
from pytest_xray.xray_plugin import XrayPlugin


def collect_report(longrepr, worker=False):
    report = pytest.TestReport('synthetic', ('synthetic.py', 0, 'case'), {}, 'passed', longrepr, 'call')
    report.test_keys = {'synthetic': ['SYN-1']}
    if worker:
        report.node = SimpleNamespace(workerinfo={
            'id': 'gw0', 'sysplatform': 'synthetic', 'version_info': (3, 12, 0), 'executable': '/synthetic/python',
        })
    plugin = XrayPlugin(SimpleNamespace(getoption=lambda name, default=None: default), None)
    plugin.pytest_runtest_logreport(report)
    return report, plugin.test_execution.as_dict()


@pytest.mark.parametrize('worker', [False, True])
def test_absent_representation_has_no_comment_and_report_is_unchanged(worker):
    report, data = collect_report(None, worker)
    assert 'comment' not in data['tests'][0]
    assert report.longrepr is None
    assert hasattr(report, 'node') == worker
    if worker:
        assert '/synthetic/python' in report.longreprtext


@pytest.mark.parametrize('worker', [False, True])
@pytest.mark.parametrize('text', ['', 'custom passing diagnostic', '[gw0] legitimate user text'])
def test_non_none_custom_representation_is_preserved(worker, text):
    report, data = collect_report(text, worker)
    comment = data['tests'][0].get('comment', '')
    assert report.longrepr == text
    if report.longreprtext:
        assert report.longreprtext in comment
    else:
        assert comment == ''


@pytest.mark.parametrize('worker', [False, True])
def test_real_comment_exact_utf8_limit_and_archive_policy_remain(worker, tmp_path):
    _, data = collect_report('界' * 120, worker)
    original = data['tests'][0]['comment']
    size = len(original.encode('utf-8'))
    assert bound_comments(data, size, None) == (data, 0)
    with pytest.raises(XrayError, match='export withheld'):
        bound_comments(data, size - 1, None)
    archive = tmp_path / 'full.json'
    bounded, count = bound_comments(data, size - 1, str(archive))
    assert count == 1 and len(bounded['tests'][0]['comment'].encode('utf-8')) <= size - 1
    assert TRUNCATION_NOTICE in bounded['tests'][0]['comment']
    assert json.loads(archive.read_text()) == data
    assert data['tests'][0]['comment'] == original


@pytest.fixture
def isolated(pytester, monkeypatch):
    for name in list(os.environ):
        if name.startswith(('XRAY_', 'PYTEST_')):
            monkeypatch.delenv(name)
    pytester.makeconftest('''
        import requests
        def blocked(*args, **kwargs):
            raise AssertionError('HTTP forbidden')
        requests.sessions.Session.request = blocked
    ''')
    return pytester


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('limit', [256, 32000])
def test_many_passing_cases_export_without_header_only_comments(isolated, workers, limit):
    isolated.makepyfile('''
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', range(250))
        def test_case(value):
            print('capture remains private')
            assert value >= 0
    ''')
    result = isolated.runpytest_subprocess(
        '-q', '-n', str(workers), '--jira-xray', '--xraypath=preview.json', '--allow-duplicate-ids',
        f'--xray-comment-limit={limit}', '--xray-case-report=cases.json',
    )
    result.assert_outcomes(passed=250)
    assert result.ret == 0
    assert json.loads((isolated.path / 'preview.json').read_text())['tests'] == [{'testKey': 'SYN-1', 'status': 'PASS'}]
    cases = json.loads((isolated.path / 'cases.json').read_text())['cases']
    assert len(cases) == 250 and all(case['status'] == 'passed' for case in cases)
    assert all('parameter_values' not in attempt for case in cases for attempt in case['attempts'])


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('captures,details', [(False, False), (True, False), (False, True), (True, True)])
def test_passing_capture_and_parameter_opt_ins_remain(isolated, workers, captures, details):
    isolated.makepyfile('''
        import logging
        import sys
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', [17], ids=['safe'])
        def test_case(value):
            print('synthetic stdout')
            print('synthetic stderr', file=sys.stderr)
            logging.warning('synthetic log')
    ''')
    args = ['-q', '-n', str(workers), '--jira-xray', '--xraypath=preview.json']
    if captures:
        args.append('--add-captures')
    if details:
        args.append('--xray-parameter-details')
    result = isolated.runpytest_subprocess(*args)
    result.assert_outcomes(passed=1)
    assert result.ret == 0
    comment = json.loads((isolated.path / 'preview.json').read_text())['tests'][0].get('comment', '')
    for text in ['synthetic stdout', 'synthetic stderr', 'synthetic log']:
        assert (text in comment) == captures
    assert ('pytest parameter case:' in comment) == details
    if details:
        assert '"value": 17' in comment
    assert ' -- Python ' not in comment


@pytest.mark.parametrize('workers', [0, 2])
def test_real_phase_skip_xfail_retry_and_custom_diagnostics_survive(isolated, workers):
    with (isolated.path / 'conftest.py').open('a') as file:
        file.write('''
import pytest
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if item.name == 'test_custom' and report.when == 'call':
        report.longrepr = 'synthetic custom passing diagnostic'
''')
    isolated.makepyfile('''
        import pytest
        @pytest.fixture
        def setup_error():
            pytest.fail('synthetic setup diagnostic')
        @pytest.fixture
        def teardown_error():
            yield
            pytest.fail('synthetic teardown diagnostic')
        @pytest.mark.xray('SYN-1')
        def test_failure():
            pytest.fail('synthetic failure diagnostic')
        @pytest.mark.xray('SYN-2')
        def test_setup(setup_error): pass
        @pytest.mark.xray('SYN-3')
        def test_teardown(teardown_error): pass
        @pytest.mark.xray('SYN-4')
        def test_skip():
            pytest.skip('synthetic skip diagnostic')
        @pytest.mark.xray('SYN-5')
        @pytest.mark.xfail(reason='expected')
        def test_xfail():
            pytest.fail('synthetic xfail diagnostic')
        @pytest.mark.xray('SYN-6')
        def test_custom(): pass
        attempts = 0
        @pytest.mark.xray('SYN-7')
        @pytest.mark.flaky(reruns=1)
        def test_retry():
            global attempts
            attempts += 1
            if attempts == 1:
                pytest.fail('synthetic retry diagnostic')
    ''')
    result = isolated.runpytest_subprocess('-q', '-n', str(workers), '--jira-xray', '--xraypath=preview.json')
    result.assert_outcomes(passed=3, failed=1, errors=2, skipped=1, xfailed=1)
    assert '1 rerun' in result.stdout.str()
    assert result.ret == 1
    data = {test['testKey']: test for test in json.loads((isolated.path / 'preview.json').read_text())['tests']}
    for number, kind in enumerate(['failure', 'setup', 'teardown', 'skip', 'xfail', 'custom passing', 'retry'], 1):
        test = data[f'SYN-{number}']
        assert f'synthetic {kind} diagnostic' in test['comment']
        assert test['status'] == ('PASS' if number == 6 else 'ABORTED' if number == 4 else 'FAIL')
        if workers:
            assert ' -- Python ' in test['comment']
