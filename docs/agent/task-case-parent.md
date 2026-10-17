# Create parent folders for requested local case reports

Continue bounded user-facing reporting work after independently accepted PR24
merges and main CI passes. Open GitHub issues were empty. Fresh installed 0.1.8
reproduction with blocked HTTP shows a passing test followed by exit 3 and no
report when --xray-case-report=artifacts/reports/cases.json has absent parents,
in serial and xdist. Xray preview/full-archive writers already create parents.

Make the case-report controller create missing parent directories at session
finish, after successful JSON serialization and before opening its owned
same-directory temporary file. Use pathlib mkdir(parents=True, exist_ok=True),
without permission changes or directory cleanup. Preserve atomic replacement,
existing-file retention, cleanup-error handling, warnings/exit semantics, schema,
privacy opt-ins/redaction, relative/home/path normalization, controller-only
writes and final session exit status. This is not configuration-time preflight,
permission bypass, transactional directory creation or race-free filesystem
validation. Parents created before a later write failure can remain. Existing
files in the parent path must not be replaced. Collect-only and unused report
options must not create directories; failed serialization must not create them.

Runtime scope only case_report.py. Replace the existing missing-parent failure
regression with a real blocking-parent-file failure, preserving its diagnostic
and exit-code assertions. Add synthetic regression coverage for nested relative
and absolute paths, passing/failing serial/xdist sessions, existing-parent and
previous-report preservation, mkdir permission errors, collect-only/worker skips,
serialization failure and later atomic-replace failure. No network or real data.

Update full beginner README, option/troubleshooting/migration sections, Unreleased
changelog/readiness and case schema guide where needed. Add one runnable nested
report example, explicitly unpublished until release. Extend only the installed
usage checker to execute and verify this fifteenth README command against a fresh
wheel, including absent parents before execution. Preserve its existing fourteen
commands and full-metadata checks. No version/dependency/workflow/permissions,
Jira/Xray aggregation, transport or native-iteration changes.

Archive prior accepted ledger, preserve unrelated files and run all five profiles,
changed-file Ruff, existing mypy and exact-head CI. Freeze one PR for fresh
parent-arranged independent review before merge; group changes for the next
milestone, do not publish now. No workplace/private data, accounts/credentials,
purchases or browser certificate bypass. Generic 8.5.3-j10/custom Automatic
mapping remains unverified live; native iterations/datasets unsupported.
Maintenance ends 2026-10-18 23:59 Asia/Dubai.

Official pathlib documentation checked 2026-10-17:
https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.mkdir
parents=True creates missing parents; exist_ok=True tolerates an existing
directory, not an existing non-directory. Normal filesystem permissions apply.
