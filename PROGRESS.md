# Current iteration — GitHub release automation

- **Task:** XRAY-RELEASE-001; branch `feat/verified-github-releases`.
- **Baseline:** 0.1.5 published from d007ade; evidence commit a02693b. PR #12 merged,
  independently accepted, public install passed 14 commands and 31 regressions.
- **Completed release:** [evidence](docs/agent/evidence/XRAY-PRODUCT-002-release-0.1.5.json).
  71 Pages files hash-verified via normal TLS. Browser ERR_CERT_AUTHORITY_INVALID
  remains a user handoff; no bypass. Artifact storage returned proxy HTTP 403.
- **PR:** https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/13 (draft).
- **Scope:** [task](docs/agent/task-release-tags.md); one iteration active.
- **Implementation:** separate post-publication workflow verifies successful
  publisher provenance, exact commit/version/notes, artifact and public PyPI hashes;
  creates a tag and matching draft, verifies assets, then publishes. Safe retries;
  no tag moves, asset replacement or PyPI republishing. Existing publisher unchanged.
- **Status:** All five profiles pass: 226 tests + 19 subtests (including
  39 new focused tests), 32 harness checks, offline validation, package/Twine, all
  14 installed README commands, strict docs/links and local desktop/mobile browser.
  Changed Python Ruff and mypy pass. Final-head hosted CI and independent review
  pending. Current digest:
  `8fcc167305af4a585cf7daf8b6ff5278dd1edc63d8913e5061b066b224688e74`. No real tags or Releases created by this work.
- **Permission gate:** new job requests `actions: read` and `contents: write` on
  existing GITHUB_TOKEN. Explicit confirmation required before enabling/merge.
- **Next:** `python tools/agent.py preflight`; verify final hosted CI, obtain
  independent review and permission confirmation. Do not merge or enable beforehand.

Never bypass browser certificate/security errors; hand blocked browser checks to
the user. No workplace server/data, new tokens/accounts, or persistent access changes.


## Added user scope: measured coverage and status badges

Evidence and review are reopened for the expanded PR; earlier receipts are
historical, not acceptance for the new content. No new release is running.
Coverage measurement of clean published 0.1.5 passed 187 tests + 19 subtests:
714/745 plugin lines (95.8%), 211/240 branches (87.9%), all 13 files. First-party
Pages snapshots avoid unavailable external badge endpoints. Existing CI gains
measurement/artifact upload with its existing read-only permissions. Updated
README requires a future unused PyPI version after independent review; 0.1.5
will never be republished. Full checks and final-head review must be repeated.

- Expanded-scope implementation: 57 focused tests, changed-file Ruff and mypy pass.
  All six live badge URLs/targets are HTTP 200 with normal TLS. GitHub Markdown
  and PyPI renderer both retain all six badges; GitHub-emitted URLs also pass.
  Pages snapshot deployment 38903707244 succeeded; all 30 coverage/status files
  match their source hashes. Snapshot files/provenance are recorded in evidence.
- Current verification: refresh all five profiles and CI for the expanded content.
  The earlier f88fb62 review head/digest is obsolete for this added scope.


## Independent review correction

Parent relayed P2 on the original f88fb62 head: final draft tag_name was unchecked.
Added checks for the intended tag before publication, returned release identity
and published state, and tag target after publication. Nine regression cases fail
on the prior code; all 66 focused release/status/docs cases now pass. Mypy and
changed-file Ruff pass. Renewed independent review is required. The docs failure
38904074570 was the separate-snapshot metadata link; the corrected README points
to the public GitHub provenance file. Full profiles/CI are being refreshed again.
