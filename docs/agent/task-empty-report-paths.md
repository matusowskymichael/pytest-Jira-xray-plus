# Reject explicit empty report paths before execution

After independently accepted PR29 is merged, main CI succeeds and its documentation
is deployed and verified, address the reproduced configuration bug: an explicit
--jira-xray --xraypath= currently runs tests and selects network upload because the
empty string is treated like an omitted export option. A synthetic probe with a
blocked requests transport confirmed a transport attempt; no real server contacted.
Empty --xray-case-report and --xray-full-report similarly disable requested outputs.

Reject an explicit empty string for all three report-path options with pytest
UsageError (exit 4) in normal execution before collection, fixtures, worker startup,
authentication or transport. Omitted defaults remain None and preserve existing
behavior. Preserve the existing collect-only early return, nonempty filenames
(including spaces), expansion conventions, path collision checks and successful
local reports/upload selection. Do not turn empty input into the current directory.
No broader URL/auth/path policy changes or new CLI flags.

Add regression tests demonstrating the baseline problem for serial and xdist
configuration, independent case reporting, full reports and option combinations;
block all transport and check collection/fixture/transport sentinels. Verify
normal omitted-option behavior and valid reports with existing tests plus focused
positive cases. Update beginner README/troubleshooting, changelog and release
readiness with explicit unreleased behavior and a safe workaround for published
0.1.9. Preserve all fifteen executable installed-guide commands and complete PyPI
metadata, privacy opt-ins and Generic/on-prem compatibility limitations.

Use all five profiles, changed-file static checks, exact-head CI and a draft PR
for fresh independent review. Keep version, dependencies, workflows, publisher,
other runtime modules and existing tests unchanged. No deployment/publication
for this candidate; no credentials, private data, workplace access or security
bypasses. Maintenance deadline October 18 19:59 UTC. One implementation in flight.
