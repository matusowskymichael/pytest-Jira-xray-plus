# Preserve exports by omitting worker-header-only comments

Authorized continuation after independently accepted PR26 merged at
a8f8ab0aaf80417d1fdc7b7ec841a978d3347e26 and main CI passed. Installed public
0.1.8 with HTTP blocked: 250 passing parametrized cases sharing one Test export
in serial, but xdist -n 2 exits 3 and withholds export because 250 worker headers
produce 36474 comment bytes above the default 32000 limit. With full archival,
export succeeds but needlessly truncates header-only text. No captures/details
were requested. Reproduction and official pytest source establish the cause.

Bounded change: XrayPlugin uses empty diagnostic text when report.longrepr is
None, avoiding pytest terminal rendering that emits an xdist header even without
a representation. Preserve non-None representations, including custom passing
text and empty representations; never strip strings, mutate reports or skip all
passing diagnostics. Preserve captures/details opt-ins, local case reporting,
statuses/phases/reruns, grouping/evidence/defects, UTF-8 limit and full archive
policy. No new flag, larger cap, dependencies, workflow or version changes.
Update the aggregation test's synthetic report to include the real longrepr
attribute; no unrelated test changes or weakened assertions.

Regressions cover serial/xdist absent diagnostics, many passing cases sharing a
key, real/custom diagnostics, failing/setup/teardown/skipped/xfail/rerun cases,
captures/details default-off and opt-in, and exact UTF-8 comment-limit boundaries
with and without archival. Synthetic inputs and blocked transport only.

Update full beginner README (parallel, privacy, troubleshooting/migration), API
reference and Unreleased changelog/readiness. Distinguish candidate from 0.1.8;
actual diagnostic text may still include worker paths and sensitive data. This
is not a general redaction guarantee. Keep all fifteen installed guide commands
and complete metadata verification. Run all five profiles, changed-file Ruff,
existing mypy and exact-head CI. Freeze a draft PR for parent-arranged independent
review before merge. After acceptance/merge assess grouped fixes as a meaningful
release milestone, not a quota; no publication in this task.

No workplace/private data, new credentials/accounts, permissions changes or
browser security bypass. Generic/custom Automatic mapping on Xray 8.5.3-j10
still needs live validation; native iterations/datasets unsupported. Maintenance
ends 2026-10-18 23:59 Asia/Dubai. Official pytest source checked 2026-10-17:
https://docs.pytest.org/en/stable/_modules/_pytest/reports.html
BaseReport.toterminal writes worker information before checking longrepr None.
