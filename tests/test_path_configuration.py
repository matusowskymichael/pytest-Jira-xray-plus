"""Report path normalization errors are usage errors, not pytest tracebacks."""

import os
import sys

import pytest

OPTIONS = ['--xray-case-report', '--xraypath', '--xray-full-report']


def arguments(option, path):
    args = [f'{option}={path}']
    if option != '--xray-case-report':
        args.append('--jira-xray')
    if option == '--xray-full-report':
        args.append('--xraypath=preview.json')
    return args


@pytest.fixture
def suite(pytester, monkeypatch):
    for key in os.environ:
        if key.startswith('XRAY_'):
            monkeypatch.delenv(key)
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


def assert_usage_error(pytester, result, option):
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    output = str(result.stdout) + str(result.stderr)
    assert f'Cannot resolve {option}' in output
    assert 'INTERNALERROR' not in output
    assert 'Traceback' not in output
    for filename in ('collection-started', 'fixture-started', 'transport-called', 'preview.json'):
        assert not (pytester.path / filename).exists()


@pytest.mark.parametrize('option', OPTIONS)
@pytest.mark.parametrize('workers', [0, 2])
def test_unresolvable_home_is_usage_error(suite, option, workers):
    path = '~xray-synthetic-no-such-user-64fb11/report.json'
    args = arguments(option, path)
    if workers:
        args += ['-n', str(workers)]
    result = suite.runpytest_subprocess(*args)
    assert_usage_error(suite, result, option)
    assert 'Could not determine home directory' in str(result.stderr)


@pytest.mark.parametrize('option', OPTIONS)
@pytest.mark.parametrize('error', ['PermissionError', 'RuntimeError'])
@pytest.mark.parametrize('workers', [0, 2])
def test_resolution_failure_stops_before_execution(suite, option, error, workers):
    conftest = suite.path / 'conftest.py'
    with conftest.open('a') as stream:
        stream.write(f'''
original_resolve = Path.resolve
def resolve(path, *args, **kwargs):
    if path.name == 'blocked-report.json':
        raise {error}('synthetic path failure')
    return original_resolve(path, *args, **kwargs)
Path.resolve = resolve
''')
    args = arguments(option, 'blocked-report.json')
    if workers:
        args += ['-n', str(workers)]
    result = suite.runpytest_subprocess(*args)
    assert_usage_error(suite, result, option)
    assert 'synthetic path failure' in str(result.stderr)


@pytest.mark.parametrize('option', OPTIONS)
def test_real_symlink_loop_retains_python_version_boundary(suite, option):
    (suite.path / 'loop').symlink_to('loop')
    result = suite.runpytest_subprocess(*arguments(option, 'loop/report.json'))
    if sys.version_info < (3, 13):
        assert_usage_error(suite, result, option)
    else:
        # Non-strict resolution leaves the loop for the existing writer boundary.
        assert result.ret == pytest.ExitCode.INTERNAL_ERROR
        assert (suite.path / 'fixture-started').exists()
        assert 'INTERNALERROR>' not in str(result.stdout) + str(result.stderr)
    assert not (suite.path / 'transport-called').exists()


@pytest.mark.parametrize('option', OPTIONS)
def test_valid_home_expansion_still_writes_report(suite, monkeypatch, option):
    monkeypatch.setenv('HOME', str(suite.path))
    result = suite.runpytest_subprocess(*arguments(option, '~/report.json'))
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK
    assert (suite.path / 'report.json').exists()
    assert not (suite.path / 'transport-called').exists()


@pytest.mark.parametrize('option', OPTIONS)
def test_environment_expansion_conventions_preserved(suite, monkeypatch, option):
    monkeypatch.setenv('SYNTHETIC_REPORT_PATH', 'expanded.json')
    result = suite.runpytest_subprocess(*arguments(option, '$SYNTHETIC_REPORT_PATH'))
    result.assert_outcomes(passed=1)
    expected = '$SYNTHETIC_REPORT_PATH' if option == '--xray-case-report' else 'expanded.json'
    assert (suite.path / expected).exists()
    assert not (suite.path / 'transport-called').exists()


def test_normalized_collisions_still_rejected(suite, monkeypatch):
    monkeypatch.setenv('SYNTHETIC_REPORT_PATH', str(suite.path / 'same.json'))
    result = suite.runpytest_subprocess('--xray-case-report=same.json', '--xraypath=$SYNTHETIC_REPORT_PATH')
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert 'Report paths must be different' in str(result.stderr)
    assert not (suite.path / 'collection-started').exists()


def test_collect_only_retains_early_return(suite):
    result = suite.runpytest_subprocess(
        '--collect-only', '--xray-case-report=~xray-synthetic-no-such-user-64fb11/report.json'
    )
    assert result.ret == pytest.ExitCode.OK
    assert not (suite.path / 'fixture-started').exists()
    assert not (suite.path / 'transport-called').exists()


def test_unexpected_resolution_exception_is_not_reclassified(suite):
    with (suite.path / 'conftest.py').open('a') as stream:
        stream.write('''
original_resolve = Path.resolve
def resolve(path, *args, **kwargs):
    if path.name == 'blocked-report.json':
        raise TypeError('synthetic programming error')
    return original_resolve(path, *args, **kwargs)
Path.resolve = resolve
''')
    result = suite.runpytest_subprocess('--xray-case-report=blocked-report.json')
    assert result.ret == pytest.ExitCode.INTERNAL_ERROR
    assert 'TypeError: synthetic programming error' in str(result.stderr)
    assert not (suite.path / 'collection-started').exists()
