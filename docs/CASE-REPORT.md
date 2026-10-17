# Case audit report for Jira/Xray integration (schema version 1)

This report helps investigate the individual pytest cases behind aggregate Jira
Test Run results. It is an audit/debugging facility within the integration.

`pytest --xray-case-report=cases.json` writes a local JSON report without
requiring Jira markers, credentials, `--jira-xray`, or duplicate-ID overrides.
It has no transport. Do not submit this schema to Xray's import endpoint.

The model in `case_results.py` depends only on Python's standard library.
`case_report.py` adapts pytest reports to it and writes once on the controller
at session end. The report preserves each executed node ID as a distinct case,
pytest's effective parameter ID (`callspec.id`), and all observed attempts.
User-supplied IDs are retained as pytest resolves them; duplicate IDs receive
pytest's suffixes. Non-parametrized tests have `parameter_id: null`.

Each attempt stores its reporting worker and an ordered phase list. Each phase
has `phase`, normalized `outcome`, raw `pytest_outcome`, and duration in seconds.
The adapter snapshots the original outcome before rerunfailures changes its
raw report outcome to `rerun`. Thus a retry retains `outcome: failed` or `error`
with `pytest_outcome: rerun`, rather than replacing it with the eventual pass.

## Parameter privacy

Parameter values are **absent by default**. `--xray-case-values` separately opts
into scalar values: string, boolean, integer, finite float and null. Other
values get a placeholder; objects are not repr'd and containers are not traversed.
No assertion text, traceback, capture, skip reason or xfail reason is stored.
However, pytest node IDs/parameter IDs may themselves contain values; choose
safe explicit IDs. This report is not a redaction guarantee. The older
`--xray-parameter-details` comment fallback is a separate opt-in that includes
scalar values; enabling a case report does not enable that fallback.

## Optional redacted identities

`--xray-case-redact-identities` replaces node IDs with `case-1`, `case-2`, etc.,
and parameter IDs with corresponding opaque aliases in this offline file.
The controller assigns aliases, so retry grouping and worker ownership survive.
Aliases are local to one run, follow arrival order, and cannot be used to match
cases across runs. Original IDs are not included in this file. Combining this
mode with `--xray-case-values` is rejected to avoid accidentally reintroducing
values. Original identities still exist inside pytest, worker communication,
console output, other reporters and any separately enabled Xray comment output.
This option redacts only the offline case report, not the entire test process.
Two-worker and local failed-then-passed reruns exercise this mode in tests.

## Aggregation rules

- Every received phase is appended. A setup phase starts an attempt; teardown
  closes it. A phase without a current attempt starts an incomplete observation.
  Grouping uses `(nodeid, worker_id)` so workers cannot overwrite one another.
- Attempt numbers are local to a case, in controller observation order. They
  are not globally stable execution IDs or cross-session retry identifiers.
- Failed call, setup/teardown error, strict XPASS, or an otherwise unclassified
  `rerun` makes an attempt failed. Failure takes priority over skips and passes.
- Skip and XFAIL summarize as skipped; non-strict XPASS summarizes as passed.
  Their exact normalized outcomes remain available in phase records. Strict
  XPASS is recognized from pytest's standard `[XPASS(strict)]` representation;
  a nonstandard failure representation remains a failure, not a pass.
- A passing call requires a teardown observation for a complete passed attempt.
  Unknown phase outcomes or unfinished non-failing attempts are incomplete.
- Across attempts: failed > incomplete > skipped > passed. A failure followed
  by a successful retry therefore remains failed in the case summary. The
  separate `pytest_exit_status` records pytest's actual session result, which
  may be zero after successful reruns. This summary does not alter pytest's
  exit code; report-write failure does (INTERNAL_ERROR).

Cases are sorted by node ID. Attempts/phases retain arrival order. With xdist,
arrival order across workers may vary. Output uses a temporary file and atomic
replacement; an unwritable destination is reported and exits nonzero. Published
0.1.8 requires parent directories to exist. The unreleased candidate creates
missing parents after successful serialization, on the controller at write time.
Normal permissions still apply; a file blocking a parent path is not replaced.
New directories may remain after a later write failure. Collect-only and workers
do not create report directories. A previous complete file can remain after a write
failure: callers must check exit status. Reusing a path replaces the previous
session report, not appends to it; choose separate paths for separate runs.

## Exercised scope and limits

Tested on Python 3.12, pytest 9.1.1, pytest-xdist 3.8.0 and
pytest-rerunfailures 16.7: ordinary execution, two-worker load scheduling,
`--dist=each` with the same node on both workers, failed-call reruns locally and
with two workers, and a setup-failure rerun locally. Tests cover phase errors,
skip/XFAIL/XPASS, duplicate parameter IDs, sensitive-value exclusion, write
errors and simultaneous legacy Xray JSON output.

This is not a claim of compatibility with every plugin/version or scheduler.
Worker crashes/restarts, teardown-failure reruns, pytest-repeat, subtests,
arbitrary third-party retry plugins, and hard process kills are not exercised.
Only received test reports are represented: deselected/unexecuted cases,
collection errors and worker crashes do not gain fabricated case results.
Session exit status remains essential when interpreting partial output.
The adapter does not change the inherited legacy Xray publisher's rerun or
status semantics. No native Xray reporting is implied by these offline tests.
