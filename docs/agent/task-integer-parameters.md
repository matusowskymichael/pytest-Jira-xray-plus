# Preserve reports when integer parameter values exceed Python's conversion limit

Continue bounded correctness work after accepted PR #25 merges and main CI passes.
Fresh installed 0.1.8 reproduction with synthetic explicit pytest IDs and blocked
HTTP shows value=10**5000 breaks opt-in serialization under Python's default
4,300-digit limit. Local case-values runs both passing tests but loses the entire
case report and exits 3; legacy parameter-details stops after the first case with
INTERNALERROR/exit 3. No Jira/server input is involved.

Change only case_report.py's shared scalar_values conversion policy: exact builtin
integers that Python refuses to convert to decimal at capture time receive the
existing unsupported-value placeholder. Probe only exact builtin int values and
catch the expected ValueError; preserve representable integers as integers and
all existing exact-type/string/bool/null/finite-float/unsupported-container rules.
Never invoke arbitrary user str/repr/int methods, traverse containers, mutate
input params, alter Python's interpreter limit or introduce a custom fixed cap.
The same helper protects local --xray-case-values and --xray-parameter-details.
Default privacy, explicit IDs, schema, statuses, reruns, grouping, paths, transport
and unrelated failures remain unchanged. This is a capture-time safeguard, not a
guarantee against later user-hook data or interpreter-policy changes.

Regression coverage: positive/negative values beyond the active limit with
ordinary companion cases, serial/xdist, local values/legacy comments/both/default
off; complete report retention and all tests executed. Synthetic subprocess limits
may be configured consistently for controller/workers to keep fixtures small.
Direct tests cover threshold boundary values, configurable limits, unchanged
scalar types/input dict and hostile scalar subclasses without invoking methods.
Any test-adjusted interpreter setting must be restored; production code never
changes it. Use explicit descriptive pytest IDs so collection itself never tries
to stringify the huge value. Block transport; no private data.

Update full beginner README, value-capture and troubleshooting/migration guidance,
schema guide, Unreleased changelog/readiness. Clearly distinguish candidate from
0.1.8 and explain the placeholder with descriptive-ID guidance; do not recommend
turning off interpreter safeguards. Retain all fifteen runnable guide commands
and full metadata verification. No version/dependency/workflow/publisher changes.
Archive completed ledger, preserve unrelated source/tests/tools and run all five
profiles, changed-file Ruff, existing mypy and exact-head CI. Freeze one PR for
parent-arranged independent review before merge; group for the next milestone,
no immediate publication. No workplace/private data, new accounts/credentials,
purchases/permissions or browser bypass. Live Generic 8.5.3-j10/custom Automatic
mapping remains unverified; native iterations/datasets unsupported. Maintenance
ends 2026-10-18 23:59 Asia/Dubai.

Official Python 3.12 docs checked 2026-10-17:
https://docs.python.org/3.12/library/stdtypes.html#integer-string-conversion-length-limitation
https://docs.python.org/3.12/library/json.html#json.JSONEncoder
Builtin integers have arbitrary precision, but decimal conversion can raise
ValueError under the interpreter's digit limit. JSON number output is affected;
this change preserves the other observations instead of losing the report.
