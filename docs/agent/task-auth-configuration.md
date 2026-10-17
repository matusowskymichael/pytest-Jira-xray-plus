# Classify authentication configuration errors as pytest usage errors

After independently accepted PR19, continue the next bounded improvement without
publishing a new version for count. No current open GitHub issues were returned.
Synthetic reproduction shows missing XRAY_API_BASE_URL raises XrayError during
pytest_configure, producing INTERNALERROR/exit3 instead of a concise usage error.
The existing helpers likewise reject missing auth variables and absent CA files.

Change only plugin.py to translate expected XrayError from authentication setup
into pytest.UsageError, keeping its actionable diagnostic and suppressing the
internal traceback. Stop before collection, fixtures, authentication/import HTTP,
or report generation. Preserve helper API exceptions, auth selection/precedence,
TLS settings, successful publisher construction and runtime HTTP error handling.
Do not broaden exception catches or validate new URL/credential policies here.
Offline preview/local-only and collect-only must remain credential-free.

Add synthetic subprocess regressions for basic/token/cloud configuration failures
with serial/xdist commands, transport/collection sentinels and secret-output checks;
retain existing successful auth and upload tests. Add no live access. Update full
beginner README, troubleshooting, migration/exit-code notes and Unreleased changelog,
clearly separating candidate behavior from published0.1.7. Keep PR19 cleanup fix
unreleased and group useful work into a future separately reviewed milestone.

Run all five profiles, all14 installed README commands/full metadata, changed-file
Ruff/mypy and exact-head CI. Archive the accepted prior ledger, preserve unrelated
source/tests/tooling/dependencies/version/workflows/permissions, then freeze a PR
for parent-arranged independent review before merge. One active task through
2026-10-18 23:59 Asia/Dubai. No workplace/private data, credentials/accounts/purchases,
permission expansion or browser-security bypass. Generic Xray8.5.3-j10/custom
Automatic mapping remains unverified live; native iterations/datasets unsupported.

Official pytest API/exit-code documentation checked 2026-10-17:
https://docs.pytest.org/en/stable/reference/reference.html#pytest.UsageError
https://docs.pytest.org/en/stable/reference/exit-codes.html
Usage errors use exit4; internal errors use exit3. This change deliberately alters
the configuration failure exit code, not test outcomes or post-run upload errors.
