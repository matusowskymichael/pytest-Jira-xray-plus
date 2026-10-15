"""Offline integration coverage for the parameter-details prototype."""

import json

import pytest


def run_cases(pytester, source, *args):
    pytester.makepyfile(source)
    pytester.makeconftest("""
        import requests
        import pytest
        def blocked(*args, **kwargs):
            raise AssertionError('Network transport forbidden in regression tests')
        @pytest.fixture(autouse=True)
        def no_network(monkeypatch):
            monkeypatch.setattr(requests.sessions.Session, 'request', blocked)
    """)
    report = pytester.path / 'xray.json'
    result = pytester.runpytest('--jira-xray', '--allow-duplicate-ids', f'--xraypath={report}', *args)
    return result, json.loads(report.read_text())['tests']


def entries(test):
    text = test['comment'].removesuffix('{noformat}')
    return [
        json.loads(line.split('pytest parameter case: ', 1)[1])
        for line in text.splitlines()
        if 'pytest parameter case: ' in line
    ]


@pytest.mark.parametrize('cloud', [False, True])
@pytest.mark.parametrize('values', ['[0, 1]', '[1, 0]'])
def test_mixed_outcomes_preserve_each_case(pytester, cloud, values):
    result, tests = run_cases(
        pytester,
        f"""
        import pytest
        @pytest.mark.xray(['SYN-1', 'SYN-2'])
        @pytest.mark.parametrize('value', {values})
        def test_case(value):
            assert value == 1
    """,
        '--xray-parameter-details',
        *(['--cloud'] if cloud else []),
    )
    result.assert_outcomes(passed=1, failed=1)
    assert len(tests) == 2
    for test in tests:
        assert test['status'] == ('FAILED' if cloud else 'FAIL')
        cases = entries(test)
        assert {c['parameters']['value'] for c in cases} == {0, 1}
        assert {c['pytest_outcome'] for c in cases} == {'passed', 'failed'}
        assert len({c['nodeid'] for c in cases}) == 2
        assert 'iterations' not in test


@pytest.mark.parametrize('workers', [0, 2])
def test_passing_cases_custom_ids_and_fixture_parameters(pytester, workers):
    result, tests = run_cases(
        pytester,
        """
        import pytest
        @pytest.fixture(params=['alpha', 'βeta'], ids=['first', 'second'])
        def word(request):
            return request.param
        @pytest.mark.xray('SYN-1')
        def test_case(word):
            assert word
    """,
        '--xray-parameter-details',
        '-n',
        str(workers),
    )
    result.assert_outcomes(passed=2)
    cases = entries(tests[0])
    assert {c['parameters']['word'] for c in cases} == {'alpha', 'βeta'}
    assert len(cases) == 2
    assert tests[0]['status'] == 'PASS'


def test_phase_failures_and_skip_are_retained(pytester):
    result, tests = run_cases(
        pytester,
        """
        import pytest
        @pytest.fixture
        def lifecycle(request):
            if request.param == 'setup':
                pytest.fail('synthetic setup error')
            yield
            if request.param == 'teardown':
                pytest.fail('synthetic teardown error')
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('lifecycle', ['setup', 'teardown', 'skip', 'pass'], indirect=True)
        def test_case(lifecycle, request):
            if request.node.callspec.params['lifecycle'] == 'skip':
                pytest.skip('synthetic skip')
    """,
        '--xray-parameter-details',
    )
    result.assert_outcomes(passed=2, skipped=1, errors=2)
    cases = entries(tests[0])
    assert {(c['parameters']['lifecycle'], c['phase'], c['pytest_outcome']) for c in cases} == {
        ('setup', 'setup', 'failed'),
        ('teardown', 'call', 'passed'),
        ('teardown', 'teardown', 'failed'),
        ('skip', 'call', 'skipped'),
        ('pass', 'call', 'passed'),
    }
    # Preserve upstream skip > failure hierarchy; individual failure remains visible.
    assert tests[0]['status'] == 'ABORTED'


def test_disabled_mode_preserves_upstream_output(pytester):
    result, tests = run_cases(
        pytester,
        """
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', [10, 20])
        def test_case(value):
            assert value > 0
    """,
    )
    result.assert_outcomes(passed=2)
    assert tests == [{'testKey': 'SYN-1', 'status': 'PASS'}]


def test_non_scalar_values_do_not_invoke_repr(pytester):
    result, tests = run_cases(
        pytester,
        """
        import pytest
        class Value:
            def __repr__(self):
                raise RuntimeError('must not serialize arbitrary objects')
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', [Value()], ids=['opaque'])
        def test_case(value):
            pass
    """,
        '--xray-parameter-details',
    )
    result.assert_outcomes(passed=1)
    assert entries(tests[0])[0]['parameters']['value'] == '<unsupported value: use a descriptive pytest id>'


def test_non_parametrized_output_unchanged(pytester):
    result, tests = run_cases(
        pytester,
        """
        import pytest
        @pytest.mark.xray('SYN-1')
        def test_case():
            pass
    """,
        '--xray-parameter-details',
    )
    result.assert_outcomes(passed=1)
    assert tests == [{'testKey': 'SYN-1', 'status': 'PASS'}]


def test_server_fallback_does_not_provision_or_infer_test_type(pytester):
    result, tests = run_cases(
        pytester,
        """
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', ['one', 'two'])
        def test_automated(value):
            assert value
    """,
        '--xray-parameter-details',
    )
    result.assert_outcomes(passed=2)
    assert len(tests) == 1
    assert set(tests[0]) == {'testKey', 'status', 'comment'}
    assert tests[0]['status'] == 'PASS'
    assert len(entries(tests[0])) == 2
