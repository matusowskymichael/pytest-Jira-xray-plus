# Current iteration — verified releases and measured project status

- **Task:** XRAY-RELEASE-001; [draft PR #13](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/13).
- **Baseline:** 0.1.5 published from d007ade; public installation passed 14 README
  commands and 31 defects regressions. [Release evidence](docs/agent/evidence/XRAY-PRODUCT-002-release-0.1.5.json).
- **Current scope:** [task](docs/agent/task-release-tags.md). One iteration active;
  no parallel release, no 0.1.5 republishing. Runtime, version and publisher unchanged.
- **Release automation:** exact successful publisher/source/artifact/PyPI checks;
  matching tag, draft, assets and publication; safe retries and conflict handling.
  Reviewer P2 on f88fb62 fixed: final draft tag_name now checked, publication
  response identity/state validated, tag target rechecked. Nine added regressions
  failed on prior code; all 66 focused release/coverage/docs tests pass after fix.
- **Verification:** all five current profiles pass: 253 tests + 19 subtests,
  32 harness checks, offline validation, package/Twine, all 14 installed README
  commands, strict docs/links and local desktop/mobile browser. Changed-code Ruff
  and mypy pass. Earlier receipts are retained as historical evidence only.
- **Digest:** `86d6af06bc1a7a27a4036926905a1699415fa97cb389bcfd8dd85c4a8902becf`.
- **Hosted CI:** final-head checks must pass before acceptance; documentation run
  38904074570's metadata-link failure is fixed and local docs profile is green.
- **Coverage:** clean published 0.1.5 measured 714/745 lines (95.8%) and 211/240
  branches (87.9%), all 13 plugin files, including Python subprocesses; 187 tests
  and 19 subtests passed. [Live report](https://matusowskymichael.github.io/pytest-Jira-xray-plus/coverage/).
  CI now measures in the existing read-only Python 3.12 job and uploads an artifact.
- **Badges:** six relevant first-party/native GitHub badges; all URLs and targets
  verified HTTP 200, GitHub/PyPI renderer outputs checked, GitHub-emitted images
  verified. Pages snapshot deployment 38903707244 passed; all 30 snapshot files
  hash-verified with normal TLS. Explicit snapshot scope, timestamps and limits.
- **PyPI limitation:** new README badges need a later reviewed unused release;
  the live 0.1.5 description is immutable. The current PyPI render check is a preview.
- **Review gate:** renewed independent review required for the expanded scope and
  P2 correction. No acceptance claimed; release-job permissions remain unapproved.
- **Permission gate:** proposed job-scoped `actions: read` and `contents: write`
  on existing GITHUB_TOKEN require explicit confirmation before merge/enabling.
  No accounts/tokens, persistent access changes or extra PyPI permissions.
- **Browser handoff:** live Chromium reports ERR_CERT_AUTHORITY_INVALID; no bypass.
  User must check the live site in a trusted browser. Normal HTTPS checks passed
  separately. GitHub artifact storage returned proxy HTTP 403; actual local
  snapshot provenance is recorded instead of claiming a downloaded CI artifact.
- **Next:** `python tools/agent.py preflight`; check final CI, obtain renewed
  independent review and permission confirmation. Only then enable automation.

Never bypass browser certificate/security errors. No workplace access or private data.


## Acceptance and permission approval

Parent relayed renewed independent PASS from `/root/review_tagged_release_workflow`
for head 55385e2 / digest 86d6af06, static/evidence review only. User explicitly
answered "You may" to the scoped release-job actions:read / contents:write request.
Both records are in evidence. Acceptance is recorded; earlier pending statements
above describe preparation. Merge/backfill verification is now authorized and active.
No broader permissions or new credentials are authorized.
