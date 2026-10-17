"""Atomic report failures preserve the primary diagnostic and owned-file boundary."""

import json
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from pytest_xray.case_report import CaseReportPlugin
from pytest_xray.exceptions import XrayError
from pytest_xray.file_publisher import FilePublisher


@pytest.fixture(params=['xray', 'case'])
def writer(request, tmp_path):
    destination = tmp_path / 'report.json'
    destination.write_text('previous')
    session = SimpleNamespace(exitstatus=pytest.ExitCode.OK)
    if request.param == 'xray':
        def invoke():
            return FilePublisher(str(destination)).publish({'tests': []})
    else:
        plugin = CaseReportPlugin(SimpleNamespace(), destination)
        def invoke():
            return plugin.pytest_sessionfinish(session, session.exitstatus)
    return request.param, destination, session, invoke


def capture_failure(writer):
    kind, _, session, invoke = writer
    if kind == 'xray':
        with pytest.raises(XrayError) as caught:
            invoke()
        assert isinstance(caught.value.__cause__, PermissionError)
        assert str(caught.value.__cause__) == 'primary replacement failure'
        return caught.value.message
    with pytest.warns(pytest.PytestWarning) as caught:
        invoke()
    assert session.exitstatus == pytest.ExitCode.INTERNAL_ERROR
    assert len(caught) == 1
    return str(caught[0].message)


@pytest.mark.parametrize('cleanup_fails', [False, True])
def test_replace_failure_preserves_primary_and_previous_report(writer, monkeypatch, cleanup_fails):
    _, destination, _, _ = writer
    unrelated = destination.parent / 'unrelated.txt'
    unrelated.write_text('untouched')
    monkeypatch.setattr('os.replace', Mock(side_effect=PermissionError('primary replacement failure')))
    original_unlink = Path.unlink
    removed = []

    def unlink(path, **kwargs):
        removed.append(path)
        if cleanup_fails:
            raise PermissionError('secondary cleanup failure')
        return original_unlink(path, **kwargs)

    with monkeypatch.context() as context:
        context.setattr(Path, 'unlink', unlink)
        message = capture_failure(writer)
    assert 'primary replacement failure' in message
    assert destination.read_text() == 'previous'
    assert unrelated.read_text() == 'untouched'
    assert len(removed) == 1
    temporary = removed[0]
    assert temporary not in (destination, unrelated)
    assert temporary.parent == destination.parent
    if cleanup_fails:
        assert 'secondary cleanup failure' in message
        assert str(temporary) in message
        assert temporary.exists()
    else:
        assert not temporary.exists()
        assert 'cleanup' not in message


def test_success_does_not_unlink_replaced_temporary_name(writer, monkeypatch):
    _, destination, session, invoke = writer
    unlink = Mock(side_effect=PermissionError('unexpected cleanup'))
    with monkeypatch.context() as context:
        context.setattr(Path, 'unlink', unlink)
        invoke()
    unlink.assert_not_called()
    assert isinstance(json.loads(destination.read_text()), dict)
    assert list(destination.parent.iterdir()) == [destination]
    assert session.exitstatus == pytest.ExitCode.OK


def test_creation_failure_does_not_unlink_unowned_files(writer, monkeypatch):
    _, destination, _, _ = writer
    monkeypatch.setattr('tempfile.NamedTemporaryFile', Mock(side_effect=PermissionError('primary replacement failure')))
    unlink = Mock(side_effect=AssertionError('must not unlink unowned files'))
    with monkeypatch.context() as context:
        context.setattr(Path, 'unlink', unlink)
        message = capture_failure(writer)
    assert 'primary replacement failure' in message
    unlink.assert_not_called()
    assert destination.read_text() == 'previous'
    assert list(destination.parent.iterdir()) == [destination]


def test_cleanup_precedes_warning_promoted_to_error(tmp_path, monkeypatch):
    destination = tmp_path / 'report.json'
    destination.write_text('previous')
    plugin = CaseReportPlugin(SimpleNamespace(), destination)
    session = SimpleNamespace(exitstatus=pytest.ExitCode.OK)
    monkeypatch.setattr('os.replace', Mock(side_effect=PermissionError('primary replacement failure')))
    with pytest.raises(pytest.PytestWarning, match='primary replacement failure'), warnings.catch_warnings():
        warnings.simplefilter('error', pytest.PytestWarning)
        plugin.pytest_sessionfinish(session, session.exitstatus)
    assert session.exitstatus == pytest.ExitCode.INTERNAL_ERROR
    assert destination.read_text() == 'previous'
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize('stage', ['write', 'close'])
@pytest.mark.parametrize('cleanup_fails', [False, True])
def test_stream_failure_cleanup(writer, monkeypatch, stage, cleanup_fails):
    _, destination, _, _ = writer
    original_temporary = tempfile.NamedTemporaryFile

    @contextmanager
    def failing_stream(**kwargs):
        with original_temporary(**kwargs) as stream:
            if stage == 'write':
                stream.write = Mock(side_effect=PermissionError('primary replacement failure'))
            yield stream
            if stage == 'close':
                raise PermissionError('primary replacement failure')

    monkeypatch.setattr(tempfile, 'NamedTemporaryFile', failing_stream)
    with monkeypatch.context() as context:
        if cleanup_fails:
            context.setattr(Path, 'unlink', Mock(side_effect=PermissionError('secondary cleanup failure')))
        message = capture_failure(writer)
    assert destination.read_text() == 'previous'
    remaining = [p for p in destination.parent.iterdir() if p != destination]
    assert len(remaining) == int(cleanup_fails)
    if cleanup_fails:
        assert str(remaining[0]) in message
        assert 'secondary cleanup failure' in message


@pytest.mark.parametrize('cleanup_fails', [False, True])
def test_unexpected_exception_is_not_replaced_by_cleanup(writer, monkeypatch, cleanup_fails):
    _, destination, _, invoke = writer
    monkeypatch.setattr('os.replace', Mock(side_effect=KeyboardInterrupt('primary interruption')))
    with monkeypatch.context() as context:
        if cleanup_fails:
            context.setattr(Path, 'unlink', Mock(side_effect=PermissionError('secondary cleanup failure')))
        with pytest.raises(KeyboardInterrupt, match='primary interruption'):
            invoke()
    assert destination.read_text() == 'previous'
    remaining = [p for p in destination.parent.iterdir() if p != destination]
    assert len(remaining) == int(cleanup_fails)


@pytest.mark.parametrize('kind', ['xray', 'case'])
def test_cli_double_failure_keeps_normal_reporting_boundary(pytester, kind):
    pytester.makepyfile("import pytest\n@pytest.mark.xray('SYN-1')\ndef test_case(): pass")
    pytester.makeconftest('''
        import os
        from pathlib import Path
        original_replace = os.replace
        original_unlink = Path.unlink
        owned = set()
        def replace(source, destination):
            if Path(destination).name == 'report.json':
                owned.add(Path(source))
                raise PermissionError('primary replacement failure')
            return original_replace(source, destination)
        def unlink(path, **kwargs):
            if path in owned:
                raise PermissionError('secondary cleanup failure')
            return original_unlink(path, **kwargs)
        os.replace = replace
        Path.unlink = unlink
    ''')
    destination = pytester.path / 'report.json'
    destination.write_text('previous')
    options = ['--jira-xray', '--xraypath=report.json'] if kind == 'xray' else ['--xray-case-report=report.json']
    result = pytester.runpytest_subprocess(*options)
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.INTERNAL_ERROR
    output = str(result.stdout) + str(result.stderr)
    assert 'primary replacement failure' in output
    assert 'secondary cleanup failure' in output
    assert 'INTERNALERROR>' not in output
    assert destination.read_text() == 'previous'
