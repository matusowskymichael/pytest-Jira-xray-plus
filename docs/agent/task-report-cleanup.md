# Preserve report write errors when temporary cleanup also fails

Following verified 0.1.7 publication, a synthetic double-permission failure shows
both report writers let Path.unlink replace the primary report-writing error.
The Xray writer loses its XrayError boundary; the local writer emits its warning
and sets exit3 but then raises a raw cleanup error. Previous files survive.

Fix only src/pytest_xray/file_publisher.py and case_report.py so failed temporary
cleanup cannot mask expected serialization/write/replace failures. Keep the primary
diagnostic and existing XrayError or local warning/exit3 handling. Report secondary
cleanup failure and the owned temporary path without dumping report contents.
After successful atomic replacement, do not unlink the now-consumed temporary name.
Keep cleanup on unexpected exceptions, destination preservation and file ownership.
Do not change payloads, aggregation, upload, privacy opt-ins, dependencies, version,
workflows, permissions or publishing settings. No automatic broad cleanup.

Add synthetic regressions for both writers: replace failure with successful/failed
cleanup, successful replacement, failure before temporary creation, warnings as
errors and write/close failures as applicable. Update full beginner README,
troubleshooting, Unreleased changelog and readiness evidence without presenting
unreleased behavior as already published. Verify all five profiles, all14 installed
tutorial commands, changed-file Ruff/mypy and exact-head CI. Preserve accepted
release evidence and unrelated source/tooling via the ledger preservation map.
Return frozen PR head/digest for fresh parent-arranged independent review; no
merge/release until acceptance and final gates. One iteration at a time through
2026-10-18 23:59 Asia/Dubai. No workplace/private data, new credentials/accounts,
purchases, permissions or browser security bypass. Live Xray8.5.3-j10/custom
Automatic mapping remains unverified; native iterations/datasets unsupported.

Official API references checked 2026-10-17:
- https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
- https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink
- https://docs.python.org/3/library/os.html#os.replace
NamedTemporaryFile(delete=False) leaves removal to this caller; missing_ok ignores
missing files, not permission errors. Successful replace consumes the source name.
