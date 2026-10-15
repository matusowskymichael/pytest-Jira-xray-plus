"""Opt-in local case report; has no Xray publisher or network transport."""

import json
import math
import os
import tempfile
import warnings
from pathlib import Path

import pytest

from pytest_xray.case_results import CaseResults, PhaseResult


def scalar_values(params):
    """Do not traverse containers or invoke user serialization/repr methods."""
    return {
        name: value
        if type(value) in (str, int, bool, type(None)) or (type(value) is float and math.isfinite(value))
        else '<unsupported value: use a descriptive pytest id>'
        for name, value in params.items()
    }


def phase_outcome(report):
    if report.outcome == 'rerun':
        return 'rerun'
    if hasattr(report, 'wasxfail'):
        if report.skipped:
            return 'xfail'
        if report.passed:
            return 'xpass'
    if report.failed:
        if report.when != 'call':
            return 'error'
        if report.longreprtext.startswith('[XPASS(strict)]'):
            return 'xpass_strict'
        return 'failed'
    return report.outcome


class CaseReportPlugin:
    def __init__(self, config, path, include_values=False, redact_identities=False):
        self.config = config
        self.path = Path(path).expanduser().resolve()
        self.include_values = include_values
        self.redact_identities = redact_identities
        self._identities = {}
        self.results = CaseResults()

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        callspec = getattr(item, 'callspec', None)
        report.xray_case_metadata = {
            'parameter_id': callspec.id if callspec else None,
            'outcome': phase_outcome(report),
        }
        if self.include_values and callspec:
            report.xray_case_metadata['parameter_values'] = scalar_values(callspec.params)

    def pytest_runtest_logreport(self, report):
        if hasattr(self.config, 'workerinput'):
            return
        metadata = getattr(report, 'xray_case_metadata', {})
        nodeid = report.nodeid
        parameter_id = metadata.get('parameter_id')
        if self.redact_identities:
            nodeid = self._identities.setdefault(nodeid, f'case-{len(self._identities) + 1}')
            parameter_id = f'{nodeid}-parameters' if parameter_id is not None else None
        self.results.record(
            nodeid=nodeid,
            worker_id=getattr(report, 'worker_id', 'local'),
            parameter_id=parameter_id,
            parameter_values=metadata.get('parameter_values'),
            phase=PhaseResult(
                report.when, metadata.get('outcome', phase_outcome(report)), report.outcome, report.duration
            ),
        )

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session, exitstatus):
        if hasattr(self.config, 'workerinput'):
            return
        temporary = None
        try:
            content = json.dumps(self.results.as_dict(int(exitstatus)), indent=2, ensure_ascii=True, allow_nan=False)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content + '\n')
            os.replace(temporary, self.path)
        except (OSError, ValueError) as exc:
            session.exitstatus = pytest.ExitCode.INTERNAL_ERROR
            warnings.warn(pytest.PytestWarning(f'Could not write offline case report {self.path}: {exc}'), stacklevel=2)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
