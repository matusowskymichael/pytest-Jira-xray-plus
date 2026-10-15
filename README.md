# pytest-Jira-xray-plus

An independent Apache-2.0 fork of
[pytest-jira-xray](https://github.com/fundakol/pytest-jira-xray), based on
`6ac1117585da590001cdbc2bf261b78683c19dcb` (0.9.4 line).
**Experimental alpha 0.1.0a1**, prepared for community testing. Native per-case
Xray integration is unverified; this is not production-ready. No native iteration
or dataset support is claimed. Publication status must be checked on PyPI.

Requires Python 3.12+ and pytest 9.1.1–9.x; validated on Python 3.12 / pytest
9.1.1 only. Older inherited compatibility claims have been removed for this
initial alpha. Report bugs with synthetic reproducers via
[GitHub issues](https://github.com/matusowskymichael/pytest-Jira-xray-plus/issues).

Start with the [two-stage validation kit](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/docs/QUICK-VALIDATION.md): one offline
command, then an optional experimental sandbox-only native capability probe.

## Preserve every executed case offline

`pytest --xray-case-report=cases.json` now produces a transport-independent
JSON report: unique node IDs, effective parameter IDs, phase outcomes and all
observed attempts. A failed attempt survives a later successful retry. No Jira
markers, credentials or uploads are needed. Parameter values are excluded;
`--xray-case-values` separately opts into potentially sensitive scalar values.
IDs themselves can contain data, so use safe explicit IDs or opt into
`--xray-case-redact-identities` for per-run aliases in the offline file.

See [report schema and aggregation rules](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/docs/CASE-REPORT.md). The report is
not Xray import JSON and does not populate Jira's native iteration UI.

## Optional comment fallback

`--xray-parameter-details` retains case details in the legacy Xray Test Run
comment. This remains a **fallback**, separate from the complete local case
report. It does not create native Xray iterations or datasets, and it explicitly
opts into including scalar values. Without either feature flag, upstream
behavior is unchanged.

Upstream already rejects duplicate Jira IDs by default. With
`--allow-duplicate-ids`, it merges results and preserves failure over pass.
The baseline probe reproduces loss of individual passing-case detail, not a
last-result-wins status bug.

## Local use (no Jira required)

Use a fresh virtual environment. Do not install this fork alongside
`pytest-jira-xray`: both intentionally provide `pytest_xray` and the `xray`
pytest entry point for compatibility.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e . pytest-httpserver pytest-xdist pytest-rerunfailures
pytest examples/synthetic.py --xray-case-report=cases.json

# Optional legacy Xray JSON comment fallback (also offline):
pytest examples/synthetic.py --jira-xray --allow-duplicate-ids \
  --xray-parameter-details --xraypath=xray.json
```

The example intentionally has one failure followed by a pass. Exit code 1 is
expected. Add `--cloud` for Cloud status strings (`PASSED`/`FAILED`);
the default remains upstream's Server/DC spelling (`PASS`/`FAIL`).
When enabling `--jira-xray`, also use `--xraypath` for offline evaluation;
omitting it enables the inherited upload path. `--xray-case-report` alone
never enables that publisher.

The comment fallback leaves non-parametrized Xray results unchanged. Existing captures, defects and evidences
continue to merge. Setup/teardown errors are separate phase records, not extra
parameter cases. xdist report serialization is covered by integration tests;
parallel completion order is not guaranteed.

Values are opt-in: scalars and node IDs may contain sensitive data. Use synthetic
inputs for evaluation. Non-scalar objects receive a placeholder without calling
user `repr`; choose descriptive pytest IDs for those. Indirect fixture values
are the input parameters, not the fixture's runtime return values.

## Validation

```sh
pytest -q
python tools/reproduce.py src --details
python -m build
python -m twine check dist/*
```

The regression probe can also be run against an unmodified upstream checkout:
`python tools/reproduce.py /path/to/upstream/src`. It deliberately fails when
both passing parameter cases are absent from the report, after first proving
that a failure survives a later pass. See [validation scope](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/docs/VALIDATION.md).
Regression tests block HTTP transport; inherited integration tests use only a
localhost fake server with synthetic credentials.

## Scope and next decisions

Native iterations, dataset creation, per-iteration evidence, cross-session
attempt identity, parameter redaction and comment-size limits need further design.
See the [unexecuted native validation plan](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/docs/NATIVE-VALIDATION.md).
For the legacy Xray payload only, the original status hierarchy is retained: ABORTED outranks FAIL, so a group
containing a skip and a failure is ABORTED, with the failure visible in comments.
This prototype does not silently turn that group into PASS, but does not change
upstream's semantics to fail-dominant either. Expected failures and unexpected
passes retain upstream mappings. Publishing error exit behavior is also inherited.
The independent offline report uses the conservative failure-first rules
documented in [CASE-REPORT.md](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/docs/CASE-REPORT.md).

Read [API decision notes](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/docs/API.md), [release proposal](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/docs/RELEASE.md),
and [NOTICE](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/dev/offline-case-reporting/NOTICE). Original upstream instructions remain in `README.rst`.
