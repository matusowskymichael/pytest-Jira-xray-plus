# Reject blank upload base URLs before running tests

Continue bounded correctness work after verified 0.1.8, without a release quota.
A fresh installed 0.1.8 reproduction with blocked HTTP transport shows empty and
whitespace-only XRAY_API_BASE_URL values run the test before ending with
MissingSchema/exit 3 in basic, API-key and Cloud authentication modes.

Change only helper.py's get_base_options to reject values whose str.strip() is
empty with XrayError naming XRAY_API_BASE_URL and a corrective diagnostic. The
existing plugin boundary converts this expected setup error to pytest UsageError
(exit 4) before collection, fixtures or transport. Do not echo the value. Preserve
missing-variable diagnostics, every nonblank value byte-for-byte, credential
handling, TLS, auth precedence, runtime HTTP failures, offline exports/local-only
reports and collect-only. This is not URL-format, credential or server validation.
Do not change package version, dependencies, workflows, permissions or payloads.

Regression evidence: blank/whitespace values across all three auth modes and
serial/xdist, no collection/fixture/report/transport side effects, direct helper
XrayError, unchanged nonblank values (including values Requests may reject later),
and credential-free offline/collect-only with a blank variable present. Retain
all existing tests and preserve unrelated source, tooling and requirements.

Update the full beginner README, troubleshooting/migration, Unreleased changelog
and readiness notes, distinguishing this candidate from published 0.1.8. Run all
five profiles, all 14 installed commands/full metadata, changed-file Ruff/mypy and
exact-head CI. Freeze a PR for parent-arranged fresh independent review; no merge
before acceptance and final gates. Archive prior accepted ledger/provenance.
No workplace/private data, new accounts/credentials/purchases/permissions, or
browser certificate bypass. Generic on-prem 8.5.3-j10/custom Automatic mapping
remains unverified live; native iterations/datasets unsupported. One active task
through 2026-10-18 23:59 Asia/Dubai.

Official sources checked 2026-10-17:
https://requests.readthedocs.io/en/latest/_modules/requests/models/#PreparedRequest.prepare_url
https://docs.pytest.org/en/stable/reference/exit-codes.html
Requests prepares URLs before sending and raises MissingSchema for absent schemes;
pytest identifies exit 4 as usage error. The new guard checks only blank input;
it does not preflight remote reachability or promise a successful upload.
