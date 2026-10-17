"""Unrepresentable integer inputs must not discard otherwise valid reports."""

import json
import os
import sys
from contextlib import contextmanager

import pytest

from pytest_xray.case_report import scalar_values

PLACEHOLDER = '<unsupported value: use a descriptive pytest id>'


@contextmanager
def conversion_limit(limit):
    original = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(limit)
        yield
    finally:
        sys.set_int_max_str_digits(original)


@pytest.mark.parametrize('limit', [640, 1000])
@pytest.mark.parametrize('sign', [-1, 1])
def test_integer_boundary_respects_active_limit_without_changing_it(limit, sign):
    with conversion_limit(limit):
        valid = sign * 10 ** (limit - 1)
        oversized = sign * 10 ** limit
        params = {'valid': valid, 'oversized': oversized, 'ordinary': 17}
        result = scalar_values(params)
        assert result['valid'] is valid
        assert type(result['valid']) is int
        assert result['oversized'] == PLACEHOLDER
        assert result['ordinary'] == 17
        assert params['oversized'] is oversized
        assert sys.get_int_max_str_digits() == limit
        assert json.loads(json.dumps(result)) == result


def test_supported_scalars_keep_their_values_and_types():
    params = {'text': 'safe', 'integer': 17, 'negative': -3, 'zero': 0, 'bool': True, 'null': None, 'float': 0.5}
    result = scalar_values(params)
    assert result == params
    assert all(result[name] is value for name, value in params.items())


def test_hostile_integer_subclass_is_not_converted():
    class HostileInt(int):
        def __str__(self):
            raise AssertionError('user str must not run')

        def __repr__(self):
            raise AssertionError('user repr must not run')

        def __int__(self):
            raise AssertionError('user int must not run')

    value = HostileInt(17)
    assert scalar_values({'value': value}) == {'value': PLACEHOLDER}


def test_unsupported_values_keep_existing_placeholder_without_traversal():
    class Hostile:
        def __repr__(self):
            raise AssertionError('user repr must not run')

    container = [Hostile()]
    params = {'container': container, 'object': Hostile(), 'nan': float('nan'), 'infinite': float('inf')}
    assert scalar_values(params) == dict.fromkeys(params, PLACEHOLDER)
    assert params['container'] is container


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('sign', [-1, 1])
@pytest.mark.parametrize('mode', ['local', 'details', 'both', 'default'])
def test_large_integer_preserves_all_cases_and_opt_in_reports(pytester, monkeypatch, workers, sign, mode):
    for key in list(os.environ):
        if key.startswith(('XRAY_', 'PYTEST_')):
            monkeypatch.delenv(key)
    monkeypatch.setenv('PYTHONINTMAXSTRDIGITS', '640')
    pytester.makeconftest('''
        import requests
        def blocked(*args, **kwargs):
            raise AssertionError('HTTP forbidden')
        requests.sessions.Session.request = blocked
    ''')
    pytester.makepyfile(f'''
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', [{sign} * 10**640, 17], ids=['huge', 'ordinary'])
        def test_case(value):
            assert value != 0
    ''')
    local = mode in {'local', 'both', 'default'}
    xray = mode in {'details', 'both', 'default'}
    args = ['-q', '-n', str(workers)]
    if local:
        args += ['--xray-case-report=cases.json']
        if mode != 'default':
            args += ['--xray-case-values']
    if xray:
        args += ['--jira-xray', '--xraypath=preview.json', '--allow-duplicate-ids']
        if mode != 'default':
            args += ['--xray-parameter-details']
    result = pytester.runpytest_subprocess(*args)
    result.assert_outcomes(passed=2)
    assert result.ret == pytest.ExitCode.OK
    assert 'INTERNALERROR' not in str(result.stdout) + str(result.stderr)
    expected = {'huge': PLACEHOLDER, 'ordinary': 17}
    if local:
        data = json.loads((pytester.path / 'cases.json').read_text())
        assert data['pytest_exit_status'] == 0 and len(data['cases']) == 2
        for case in data['cases']:
            assert case['status'] == 'passed' and len(case['attempts']) == 1
            attempt = case['attempts'][0]
            assert attempt['complete'] and len(attempt['phases']) == 3
            if mode == 'default':
                assert 'parameter_values' not in attempt
            else:
                assert attempt['parameter_values'] == {'value': expected[attempt['parameter_id']]}
    if xray:
        tests = json.loads((pytester.path / 'preview.json').read_text())['tests']
        assert len(tests) == 1 and tests[0]['status'] == 'PASS'
        assert 'iterations' not in tests[0]
        if mode == 'default':
            comment = tests[0].get('comment', '')
            # xdist may add its existing worker header; parameter details stay opt-in.
            assert 'pytest parameter case:' not in comment
            assert PLACEHOLDER not in comment
            assert ('-' if sign < 0 else '') + '1' + '0' * 640 not in comment
        else:
            entries = [json.loads(line.split('pytest parameter case: ', 1)[1])
                       for line in tests[0]['comment'].splitlines() if 'pytest parameter case:' in line]
            assert len(entries) == 2
            assert {entry['nodeid'].split('[')[-1].rstrip(']'): entry['parameters']['value']
                    for entry in entries} == expected
