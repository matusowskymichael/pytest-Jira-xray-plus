"""Transport-independent, append-only execution observations (Apache-2.0)."""

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class PhaseResult:
    phase: str
    outcome: str
    pytest_outcome: str
    duration: float


def aggregate(phases: list[PhaseResult]) -> str:
    """Conservative summary; never erase an earlier failed or retried phase."""
    outcomes = {phase.outcome for phase in phases}
    if outcomes & {'failed', 'error', 'xpass_strict', 'rerun'}:
        return 'failed'
    if outcomes - {'passed', 'skipped', 'xfail', 'xpass'}:
        return 'incomplete'
    if 'skipped' in outcomes or 'xfail' in outcomes:
        return 'skipped'
    if any(phase.phase == 'call' and phase.outcome in {'passed', 'xpass'} for phase in phases):
        return 'passed'
    return 'incomplete'


@dataclass
class AttemptResult:
    number: int
    worker_id: str
    parameter_id: Optional[str]
    parameter_values: Optional[dict[str, Any]] = None
    phases: list[PhaseResult] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.parameter_values is None:
            del data['parameter_values']
        data['complete'] = any(phase.phase == 'teardown' for phase in self.phases)
        status = aggregate(self.phases)
        data['status'] = status if data['complete'] or status == 'failed' else 'incomplete'
        return data


@dataclass
class CaseResult:
    nodeid: str
    attempts: list[AttemptResult] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        statuses = {attempt.as_dict()['status'] for attempt in self.attempts}
        # An incomplete observation cannot make a finished failure disappear.
        status = next(
            (value for value in ('failed', 'incomplete', 'skipped', 'passed') if value in statuses), 'incomplete'
        )
        return {'nodeid': self.nodeid, 'status': status, 'attempts': [attempt.as_dict() for attempt in self.attempts]}


class CaseResults:
    """Keep every phase, grouping attempts by node ID and reporting worker."""

    def __init__(self) -> None:
        self.cases: dict[str, CaseResult] = {}
        self._active: dict[tuple[str, str], AttemptResult] = {}

    def record(
        self,
        nodeid: str,
        worker_id: str,
        parameter_id: Optional[str],
        phase: PhaseResult,
        parameter_values: Optional[dict[str, Any]] = None,
    ) -> None:
        case = self.cases.setdefault(nodeid, CaseResult(nodeid))
        key = (nodeid, worker_id)
        if phase.phase == 'setup' or key not in self._active:
            attempt = AttemptResult(len(case.attempts) + 1, worker_id, parameter_id, parameter_values)
            case.attempts.append(attempt)
            self._active[key] = attempt
        attempt = self._active[key]
        attempt.phases.append(phase)
        if phase.phase == 'teardown':
            del self._active[key]

    def as_dict(self, exit_status: int) -> dict[str, Any]:
        return {
            'schema_version': 1,
            'pytest_exit_status': exit_status,
            'cases': [self.cases[nodeid].as_dict() for nodeid in sorted(self.cases)],
        }
