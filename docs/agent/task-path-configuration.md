# Report path normalization failures as pytest usage errors

Following independently accepted PR20, continue bounded correctness work without
publishing for version count. No open GitHub issues were returned. Synthetic
unresolved home paths and Python3.12 symlink loops currently raise RuntimeError
inside report-path normalization, causing INTERNALERROR/exit3 for all three
report options. Expected filesystem resolution errors can escape there too.

Change only plugin.py's initial report-path normalization to convert OSError and
RuntimeError from expanduser/resolve into pytest.UsageError with the responsible
option and actionable diagnostic. Preserve non-strict resolution, duplicate-path
checks, each option's environment expansion convention, valid home/symlink paths,
collect-only behavior and existing file-writer/post-run failure handling. Do not
change authentication, payloads, version, dependencies, workflows or permissions.
Do not claim a filesystem preflight, race-free validation, universal loop detection
or successful future writes. Unexpected programming exceptions must propagate.

Regression tests use synthetic paths, mocked resolution failures and blocked
transport: all three options, serial/xdist commands, no collection/fixture/report
side effects when normalization fails, valid home/env expansion and collisions.
Keep a real symlink-loop regression aware of the Python version boundary:
3.12 raises during resolve(strict=False); 3.13+ leaves loops for existing writer
failure handling. No workplace server or private data.

Update the full beginner guide, troubleshooting/migration, Unreleased changelog
and readiness notes, clearly distinguishing candidate behavior from0.1.7 and
retaining exact compatibility limits. Run all five profiles, all14 installed
commands/full metadata, changed-file Ruff/mypy and exact-head CI. Freeze the next
PR for fresh parent-arranged independent review; no merge before acceptance and
final gates. Archive prior accepted ledger, preserve unrelated source/tests/tools.
One active iteration through2026-10-18 23:59 Asia/Dubai. No accounts, credentials,
purchases, permissions or browser security bypass. Live Generic8.5.3-j10/custom
Automatic mapping remains unverified; native iterations/datasets unsupported.

Official Python docs checked2026-10-17:
https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.resolve
https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.resolve
https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.expanduser
Python3.13 changed non-strict loop handling; unresolved home expansion still raises
RuntimeError. This task handles raised normalization errors without changing the
underlying path semantics or imposing existence checks on new report destinations.
