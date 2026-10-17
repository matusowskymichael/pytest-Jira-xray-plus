"""Nested report paths should work in clean CI workspaces without pre-creation."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from pytest_xray.case_report import CaseReportPlugin
from pytest_xray.case_results import PhaseResult


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('absolute', [False, True])
@pytest.mark.parametrize('failing', [False, True])
def test_nested_report_paths_preserve_test_outcomes(pytester, workers, absolute, failing):
    pytester.makeconftest('''
        import requests
        def blocked(*args, **kwargs):
            raise AssertionError('HTTP forbidden')
        requests.sessions.Session.request = blocked
    ''')
    pytester.makepyfile(f'def test_case(): assert {not failing!r}')
    destination = pytester.path / 'artifacts' / 'reports' / 'cases.json'
    argument = str(destination) if absolute else 'artifacts/reports/cases.json'
    assert not destination.parent.exists()
    result = pytester.runpytest_subprocess('-q', '-n', str(workers), f'--xray-case-report={argument}')
    assert result.ret == (pytest.ExitCode.TESTS_FAILED if failing else pytest.ExitCode.OK)
    data = json.loads(destination.read_text())
    assert data['schema_version'] == 1
    assert data['pytest_exit_status'] == int(result.ret)
    assert len(data['cases']) == 1
    case = data['cases'][0]
    assert case['status'] == ('failed' if failing else 'passed')
    assert len(case['attempts']) == 1 and case['attempts'][0]['complete']
    assert [p['phase'] for p in case['attempts'][0]['phases']] == ['setup', 'call', 'teardown']
    assert 'parameter_values' not in case['attempts'][0]
    assert sorted(p.name for p in destination.parent.iterdir()) == ['cases.json']


def test_existing_directory_and_report_can_be_reused(pytester):
    pytester.makepyfile('def test_case(): pass')
    destination = pytester.path / 'artifacts' / 'cases.json'
    destination.parent.mkdir()
    destination.write_text('previous report')
    sibling = destination.parent / 'keep.txt'
    sibling.write_text('keep')
    result = pytester.runpytest_subprocess(f'--xray-case-report={destination}')
    assert result.ret == pytest.ExitCode.OK
    assert json.loads(destination.read_text())['cases'][0]['status'] == 'passed'
    assert sibling.read_text() == 'keep'


@pytest.mark.parametrize('args', [[], ['--collect-only', '--xray-case-report=artifacts/reports/cases.json']])
def test_no_requested_write_means_no_directory_creation(pytester, args):
    pytester.makepyfile('def test_case(): pass')
    result = pytester.runpytest_subprocess(*args)
    assert result.ret == pytest.ExitCode.OK
    assert not (pytester.path / 'artifacts').exists()


@pytest.mark.parametrize('exit_status', [pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED])
def test_directory_creation_error_preserves_existing_report(tmp_path, monkeypatch, exit_status):
    destination = tmp_path / 'cases.json'
    destination.write_text('previous report')
    plugin = CaseReportPlugin(SimpleNamespace(), destination)
    session = SimpleNamespace(exitstatus=exit_status)
    with monkeypatch.context() as context:
        context.setattr(Path, 'mkdir', Mock(side_effect=PermissionError('synthetic denied directory')))
        with pytest.warns(pytest.PytestWarning, match='synthetic denied directory'):
            plugin.pytest_sessionfinish(session, exit_status)
    assert session.exitstatus == pytest.ExitCode.INTERNAL_ERROR
    assert destination.read_text() == 'previous report'
    assert sorted(p.name for p in tmp_path.iterdir()) == ['cases.json']


def test_failed_serialization_does_not_create_parents(tmp_path):
    destination = tmp_path / 'artifacts' / 'reports' / 'cases.json'
    plugin = CaseReportPlugin(SimpleNamespace(), destination)
    plugin.results.record('synthetic', 'local', None, PhaseResult('call', 'passed', 'passed', float('nan')))
    session = SimpleNamespace(exitstatus=pytest.ExitCode.OK)
    with pytest.warns(pytest.PytestWarning, match='Could not write offline case report'):
        plugin.pytest_sessionfinish(session, session.exitstatus)
    assert session.exitstatus == pytest.ExitCode.INTERNAL_ERROR
    assert not (tmp_path / 'artifacts').exists()


def test_worker_does_not_create_parents(tmp_path):
    destination = tmp_path / 'artifacts' / 'reports' / 'cases.json'
    plugin = CaseReportPlugin(SimpleNamespace(workerinput={}), destination)
    session = SimpleNamespace(exitstatus=pytest.ExitCode.OK)
    plugin.pytest_sessionfinish(session, session.exitstatus)
    assert session.exitstatus == pytest.ExitCode.OK
    assert not (tmp_path / 'artifacts').exists()


def test_later_replace_failure_leaves_directories_but_removes_owned_temp(tmp_path, monkeypatch):
    destination = tmp_path / 'artifacts' / 'reports' / 'cases.json'
    plugin = CaseReportPlugin(SimpleNamespace(), destination)
    session = SimpleNamespace(exitstatus=pytest.ExitCode.OK)
    monkeypatch.setattr('os.replace', Mock(side_effect=PermissionError('synthetic replacement denied')))
    with pytest.warns(pytest.PytestWarning, match='synthetic replacement denied'):
        plugin.pytest_sessionfinish(session, session.exitstatus)
    assert session.exitstatus == pytest.ExitCode.INTERNAL_ERROR
    assert destination.parent.is_dir()
    assert list(destination.parent.iterdir()) == []
