# Scale plugin result aggregation without changing exported results

After independently accepted PR23 merges and main CI passes, continue useful
bounded work. Open issues were empty. Inspection and a synthetic result-stream
benchmark show XrayPlugin scans all prior Test cases for each new key: 2k/4k/8k
unique keys take approximately 0.04/0.16/0.60 seconds on this environment, with
n(n-1)/2 key comparisons. This becomes unnecessary overhead for large suites.
Timings are illustrative, not a universal speed guarantee or a test threshold.

Change only xray_plugin.py to keep a per-instance dictionary of the aggregates
created during its report stream, keyed by existing Test key. Append each new
aggregate to the existing execution list in first-observed order and reuse the
same TestCase objects and merge method on subsequent observations. Preserve all
status mappings/precedence, comment ordering, evidence multiplicity and ownership,
defect deduplication, multi-key markers, reruns, phases and xdist behavior. Keep
TestExecution/TestCase and their public mutable-list/find APIs unchanged; no cache
inside that model. Preserve the documented final pytest_xray_results payload hook,
archival/comment limits, upload withholding and failure handling. The index costs
one extra dictionary entry per unique key. It assumes the plugin owns its live
accumulators; direct concurrent mutation of internal accumulation is not a
supported hook contract. Do not introduce a new user flag or change payload schema,
version, dependencies, workflows, credentials or permissions.

Add deterministic comparison-count regressions (not elapsed-time thresholds) for
unique and repeated keys, semantic payload comparisons across report phases and
server/Cloud mappings, model API preservation and synthetic serial/xdist rerun
exports with the final results hook. All HTTP must be blocked or localhost fake.
Record before/after benchmark method and actual measurements with the scope of
its claim. Update full README, troubleshooting/migration/performance notes,
Unreleased changelog and readiness record; retain all compatibility/privacy
limits. Do not imply improved test execution speed, bounded comment memory or
live Xray evidence. Case model/export performance is outside this scope.

Archive the completed ledger. Run all five profiles, all 14 installed README
commands/full metadata, changed-file Ruff, existing mypy and exact-head CI. Freeze
one PR for fresh parent-arranged independent review before merge. Group this and
other useful changes for a later release; no immediate publication. No workplace
server/private data, accounts/credentials/purchases/permission expansion, or
browser certificate bypass. Generic 8.5.3-j10/custom Automatic mapping remains
unverified live; native iterations/datasets unsupported. Maintenance window ends
2026-10-18 23:59 Asia/Dubai.

Official references checked 2026-10-17:
https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
https://docs.pytest.org/en/stable/reference/reference.html#pytest.hookspec.pytest_runtest_logreport
Dictionary lookup follows key equality/hash semantics; report hooks observe each
setup/call/teardown report. Output order remains the existing execution list.
