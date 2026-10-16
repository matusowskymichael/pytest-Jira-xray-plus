# Current iteration — GitHub release automation

- **Task:** XRAY-RELEASE-001; branch `feat/verified-github-releases`.
- **Baseline:** 0.1.5 published from d007ade; evidence commit a02693b. PR #12 merged,
  independently accepted, public install passed 14 commands and 31 regressions.
- **Completed release:** [evidence](docs/agent/evidence/XRAY-PRODUCT-002-release-0.1.5.json).
  71 Pages files hash-verified via normal TLS. Browser ERR_CERT_AUTHORITY_INVALID
  remains a user handoff; no bypass. Artifact storage returned proxy HTTP 403.
- **Scope:** [task](docs/agent/task-release-tags.md); one iteration active.
- **Implementation:** separate post-publication workflow verifies successful
  publisher provenance, exact commit/version/notes, artifact and public PyPI hashes;
  creates a tag and matching draft, verifies assets, then publishes. Safe retries;
  no tag moves, asset replacement or PyPI republishing. Existing publisher unchanged.
- **Status:** initial 38 synthetic tests pass. Full profiles/hosted CI and
  independent review pending. No real tags or Releases created by this work.
- **Permission gate:** new job requests `actions: read` and `contents: write` on
  existing GITHUB_TOKEN. Explicit confirmation required before enabling/merge.
- **Next:** `python tools/agent.py check --profile tests`; prepare review-ready PR.

Never bypass browser certificate/security errors; hand blocked browser checks to
the user. No workplace server/data, new tokens/accounts, or persistent access changes.
