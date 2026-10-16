# Historical alpha validation and focused review

This records the original alpha baseline, not current release/harness verification.
See [release evidence](RELEASE-READINESS.md) and [current checks](agent/testing.md).

Local validation: Python 3.12, pytest 9.1.1, pytest-xdist 3.8.0,
pytest-rerunfailures 16.7. **69 tests passed** in a fresh environment installed
from this source tree. Changed/new Python files pass Ruff; the offline
reproduction probe passes. Wheel/sdist build and metadata checks pass.
No live Jira/Xray instance was used. Inherited HTTP tests use localhost only.

Reviewed behavior:

- Only the controller records/writes the offline report. Workers attach
  serializable metadata; two-worker load and each scheduling are exercised.
- Attempt grouping uses node ID plus worker ID. Repeated setup starts a new
  attempt; phases append without overwriting. Numbers follow observed order,
  not a cross-worker chronological guarantee. Cases are sorted for output.
- Setup and teardown errors retain failed status; rerun failures are captured
  before the rerun plugin changes the raw outcome. A later pass cannot erase
  an earlier failed attempt. Interrupted non-failing observations stay incomplete.
- Redacted identity mode uses controller-assigned per-run aliases and is tested
  with local and two-worker reruns. Values cannot be enabled simultaneously.
  It does not redact pytest's console, internal transport or other reporters.
- Default plugin behavior remains opt-in. Legacy Xray JSON and offline case
  reports can coexist at different paths. Same-path configuration is rejected.
  Write errors are visible and exit nonzero.

Coverage includes mixed outcomes, setup/teardown errors, skip/XFAIL/XPASS and
strict XPASS, duplicate IDs, scalar opt-in, default omission of value/failure
text, incomplete attempts, failed-call reruns locally and with xdist, a local
setup-error rerun, and the same node executing on two workers.

Not exercised: worker crashes/restarts, teardown-failure reruns, pytest-repeat,
subtests, other retry plugins or broad Python/pytest version matrices. Native
Xray iteration integration is unverified; see NATIVE-VALIDATION.md.

Publication review excluded local logs, virtual environments, caches, build
outputs and session artifacts. High-signal secret/credential patterns were
checked in the intended files. Binary test fixtures and documentation images
were compared byte-for-byte with public upstream. Issue-shaped identifiers
are synthetic test data or public documentation identifiers. This is a focused
review, not a guarantee from a comprehensive secret-scanning product.
