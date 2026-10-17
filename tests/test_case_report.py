"""Offline subprocess tests; no employer services or credentials."""

import json

import pytest


def run_report(pytester, source, *args):
    pytester.makepyfile(source)
    pytester.makeconftest("""
        import requests
        def blocked(*args, **kwargs):
            raise AssertionError('HTTP is forbidden in offline case tests')
        requests.sessions.Session.request = blocked
    """)
    path = pytester.path / 'cases.json'
    result = pytester.runpytest_subprocess(f'--xray-case-report={path}', *args)
    return result, json.loads(path.read_text())


@pytest.mark.parametrize('workers', [0, 2])
def test_preserves_nodeids_ids_and_mixed_outcomes_without_values(pytester, workers):
    result, data = run_report(
        pytester,
        """
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('number', [0, 1], ids=['first-fails', 'last-passes'])
        def test_case(number):
            assert number == 1
    """,
        '-n',
        str(workers),
    )
    result.assert_outcomes(passed=1, failed=1)
    assert data['schema_version'] == 1
    assert data['pytest_exit_status'] == 1
    assert len(data['cases']) == 2
    by_id = {case['attempts'][0]['parameter_id']: case for case in data['cases']}
    assert by_id['first-fails']['status'] == 'failed'
    assert by_id['last-passes']['status'] == 'passed'
    assert len({case['nodeid'] for case in data['cases']}) == 2
    for case in data['cases']:
        attempt = case['attempts'][0]
        assert attempt['parameter_id'] in case['nodeid']
        assert 'parameter_values' not in attempt
        assert attempt['complete'] is True
        assert [phase['phase'] for phase in attempt['phases']] == ['setup', 'call', 'teardown']
        assert attempt['worker_id'].startswith('gw') if workers else attempt['worker_id'] == 'local'


def test_setup_teardown_errors_are_not_overwritten(pytester):
    result, data = run_report(
        pytester,
        """
        import pytest
        @pytest.fixture(params=['setup', 'teardown', 'ok'])
        def resource(request):
            if request.param == 'setup':
                pytest.fail('synthetic setup failure')
            yield
            if request.param == 'teardown':
                pytest.fail('synthetic teardown failure')
        def test_case(resource):
            pass
    """,
    )
    result.assert_outcomes(passed=2, errors=2)
    by_id = {case['attempts'][0]['parameter_id']: case for case in data['cases']}
    assert {key: value['status'] for key, value in by_id.items()} == {
        'setup': 'failed',
        'teardown': 'failed',
        'ok': 'passed',
    }
    assert [(p['phase'], p['outcome']) for p in by_id['teardown']['attempts'][0]['phases']] == [
        ('setup', 'passed'),
        ('call', 'passed'),
        ('teardown', 'error'),
    ]
    assert by_id['setup']['attempts'][0]['phases'][0]['outcome'] == 'error'


def test_skip_xfail_xpass_and_strict_xpass(pytester):
    result, data = run_report(
        pytester,
        """
        import pytest
        @pytest.mark.parametrize('value', [
            pytest.param(0, id='skip', marks=pytest.mark.skip(reason='synthetic')),
            pytest.param(0, id='xfail', marks=pytest.mark.xfail(reason='synthetic')),
            pytest.param(1, id='xpass', marks=pytest.mark.xfail(reason='synthetic')),
            pytest.param(1, id='strict', marks=pytest.mark.xfail(reason='synthetic', strict=True)),
        ])
        def test_case(value):
            assert value
    """,
    )
    result.assert_outcomes(skipped=1, xfailed=1, xpassed=1, failed=1)
    by_id = {case['attempts'][0]['parameter_id']: case for case in data['cases']}
    expected = {
        'skip': ('skipped', 'skipped'),
        'xfail': ('skipped', 'xfail'),
        'xpass': ('passed', 'xpass'),
        'strict': ('failed', 'xpass_strict'),
    }
    for key, (status, outcome) in expected.items():
        assert by_id[key]['status'] == status
        assert outcome in [phase['outcome'] for phase in by_id[key]['attempts'][0]['phases']]


def test_scalar_values_require_separate_opt_in(pytester):
    result, data = run_report(
        pytester,
        """
        import pytest
        class Opaque:
            def __repr__(self):
                raise AssertionError('do not serialize arbitrary objects')
        @pytest.mark.parametrize('value', ['synthetic-value', Opaque(), float('nan')],
                                 ids=['text', 'opaque', 'nonfinite'])
        def test_case(value):
            pass
    """,
        '--xray-case-values',
    )
    result.assert_outcomes(passed=3)
    by_id = {c['attempts'][0]['parameter_id']: c['attempts'][0] for c in data['cases']}
    assert by_id['text']['parameter_values'] == {'value': 'synthetic-value'}
    for key in ('opaque', 'nonfinite'):
        assert by_id[key]['parameter_values']['value'].startswith('<unsupported value')


@pytest.mark.parametrize('workers', [0, 2])
def test_rerun_keeps_failed_attempt_and_later_pass(pytester, workers):
    result, data = run_report(
        pytester,
        """
        import pytest
        attempts = {}
        @pytest.mark.parametrize('value', ['alpha', 'beta'])
        def test_case(value):
            attempts[value] = attempts.get(value, 0) + 1
            assert attempts[value] > 1
    """,
        '--reruns=1',
        '-n',
        str(workers),
    )
    assert result.parseoutcomes() == {'passed': 2, 'rerun': 2}
    assert data['pytest_exit_status'] == 0
    for case in data['cases']:
        assert case['status'] == 'failed'
        assert len(case['attempts']) == 2
        assert [a['number'] for a in case['attempts']] == [1, 2]
        assert [a['status'] for a in case['attempts']] == ['failed', 'passed']
        assert any(p['pytest_outcome'] == 'rerun' and p['outcome'] == 'failed' for p in case['attempts'][0]['phases'])


def test_xdist_each_keeps_same_node_from_both_workers(pytester):
    result, data = run_report(
        pytester,
        """
        import pytest
        @pytest.mark.parametrize('value', [1], ids=['same-id'])
        def test_case(value):
            pass
    """,
        '-n',
        '2',
        '--dist=each',
    )
    result.assert_outcomes(passed=2)
    assert len(data['cases']) == 1
    attempts = data['cases'][0]['attempts']
    assert len(attempts) == 2
    assert {a['worker_id'] for a in attempts} == {'gw0', 'gw1'}
    assert all(len(a['phases']) == 3 and a['complete'] for a in attempts)


def test_opt_in_and_invalid_configuration(pytester):
    pytester.makepyfile('def test_case(): pass')
    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
    assert not (pytester.path / 'cases.json').exists()
    result = pytester.runpytest_subprocess('--xray-case-values')
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result = pytester.runpytest_subprocess('--xray-case-report=same.json', '--xraypath=same.json')
    assert result.ret == pytest.ExitCode.USAGE_ERROR


def test_write_failure_is_visible_and_changes_exit_code(pytester):
    pytester.makepyfile('def test_case(): pass')
    parent_file = pytester.path / 'blocked-parent'
    parent_file.write_text('existing file must survive')
    result = pytester.runpytest_subprocess('--xray-case-report=blocked-parent/cases.json')
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.INTERNAL_ERROR
    assert 'Could not write offline case report' in str(result.stdout) + str(result.stderr)
    assert parent_file.read_text() == 'existing file must survive'


def test_rerun_setup_failure_retained(pytester):
    result, data = run_report(
        pytester,
        """
        import pytest
        attempts = 0
        @pytest.fixture
        def resource():
            global attempts
            attempts += 1
            if attempts == 1:
                pytest.fail('synthetic setup failure')
        def test_case(resource):
            pass
    """,
        '--reruns=1',
    )
    assert result.parseoutcomes() == {'passed': 1, 'rerun': 1}
    case = data['cases'][0]
    assert case['status'] == 'failed'
    assert len(case['attempts']) == 2
    assert case['attempts'][0]['phases'][0]['outcome'] == 'error'
    assert case['attempts'][1]['status'] == 'passed'


def test_default_excludes_values_and_failure_text_and_disambiguates_duplicate_ids(pytester):
    result, data = run_report(
        pytester,
        """
        import pytest
        @pytest.mark.parametrize('value', ['synthetic-secret-a', 'synthetic-secret-b'], ids=['same', 'same'])
        def test_case(value):
            assert value == 'different'
    """,
    )
    result.assert_outcomes(failed=2)
    assert len(data['cases']) == 2
    assert len({case['nodeid'] for case in data['cases']}) == 2
    assert len({case['attempts'][0]['parameter_id'] for case in data['cases']}) == 2
    assert 'synthetic-secret' not in json.dumps(data)


def test_case_report_can_coexist_with_legacy_xray_file(pytester):
    xray_path = pytester.path / 'xray.json'
    result, data = run_report(
        pytester,
        """
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', [0, 1])
        def test_case(value):
            assert value == 1
    """,
        '--jira-xray',
        '--allow-duplicate-ids',
        f'--xraypath={xray_path}',
    )
    result.assert_outcomes(passed=1, failed=1)
    assert len(data['cases']) == 2
    xray = json.loads(xray_path.read_text())
    assert len(xray['tests']) == 1
    assert xray['tests'][0]['status'] == 'FAIL'
    assert 'iterations' not in xray['tests'][0]


@pytest.mark.parametrize('workers', [0, 2])
def test_redacted_identities_hide_ids_but_preserve_cases_and_attempts(pytester, workers):
    result, data = run_report(
        pytester,
        """
        import pytest
        attempts = {}
        @pytest.mark.parametrize('value', ['private-a', 'private-b'], ids=['private-id-a', 'private-id-b'])
        def test_private_function(value):
            attempts[value] = attempts.get(value, 0) + 1
            assert attempts[value] > 1
    """,
        '--xray-case-redact-identities',
        '--reruns=1',
        '-n',
        str(workers),
    )
    assert result.parseoutcomes() == {'passed': 2, 'rerun': 2}
    assert 'private' not in json.dumps(data)
    assert {c['nodeid'] for c in data['cases']} == {'case-1', 'case-2'}
    for case in data['cases']:
        assert case['status'] == 'failed'
        assert len(case['attempts']) == 2
        assert {a['parameter_id'] for a in case['attempts']} == {case['nodeid'] + '-parameters'}
        assert [a['number'] for a in case['attempts']] == [1, 2]


def test_redacted_mode_rejects_explicit_values(pytester):
    pytester.makepyfile('def test_case(): pass')
    result = pytester.runpytest_subprocess(
        '--xray-case-report=cases.json', '--xray-case-redact-identities', '--xray-case-values'
    )
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert not (pytester.path / 'cases.json').exists()
