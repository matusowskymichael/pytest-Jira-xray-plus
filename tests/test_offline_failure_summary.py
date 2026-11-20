"""Offline export failures must not look like failed Jira uploads."""

import json

import pytest


@pytest.fixture
def offline_case(pytester):
    pytester.makeconftest('''
        import requests
        def pytest_configure(config):
            def blocked(*args, **kwargs):
                raise AssertionError('Offline export attempted HTTP')
            requests.sessions.Session.request = blocked
    ''')
    return pytester


@pytest.mark.parametrize('workers', [False, True], ids=['serial', 'xdist'])
@pytest.mark.parametrize('test_passes', [False, True], ids=['failed-test', 'passed-test'])
@pytest.mark.parametrize('destination_kind', ['directory', 'file-parent'])
def test_offline_write_failure_summary(offline_case, workers, test_passes, destination_kind):
    runner = offline_case
    runner.makepyfile(f"import pytest\n@pytest.mark.xray('SYN-1')\ndef test_case(): assert {test_passes}")
    output = runner.path / 'output'
    output.mkdir()
    sentinel = output / 'existing'
    sentinel.write_text('preserve me')
    destination = output if destination_kind == 'directory' else sentinel / 'report.json'
    args = ['--jira-xray', f'--xraypath={destination}']
    if workers:
        args += ['-n', '2']
    result = runner.runpytest_subprocess(*args)
    result.assert_outcomes(passed=int(test_passes), failed=int(not test_passes))
    assert result.ret == (pytest.ExitCode.INTERNAL_ERROR if test_passes else pytest.ExitCode.TESTS_FAILED)
    text = str(result.stdout) + str(result.stderr)
    assert 'Xray file export' in text
    assert 'Could not export Xray results to file!' in text
    assert 'Cannot export Xray results to file:' in text
    assert 'Could not publish results to Jira XRAY!' not in text
    assert 'Offline export attempted HTTP' not in text
    assert 'INTERNALERROR>' not in text
    assert sentinel.read_text() == 'preserve me'
    assert list(output.iterdir()) == [sentinel]


@pytest.mark.parametrize('workers', [False, True], ids=['serial', 'xdist'])
def test_successful_offline_export_summary_unchanged(offline_case, workers):
    runner = offline_case
    runner.makepyfile("import pytest\n@pytest.mark.xray('SYN-1')\ndef test_case(): pass")
    destination = runner.path / 'output' / 'report.json'
    args = ['--jira-xray', f'--xraypath={destination}']
    if workers:
        args += ['-n', '2']
    result = runner.runpytest_subprocess(*args)
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK
    assert 'Generated XRAY execution report file:' in str(result.stdout)
    assert 'Could not' not in str(result.stdout)
    assert json.loads(destination.read_text())['tests'][0]['testKey'] == 'SYN-1'
