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
