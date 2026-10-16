# Current iteration — publish shared README badges in 0.1.6

- **Task:** XRAY-RELEASE-002; branch `release/0.1.6-status-badges`.
- **Baseline:** PR #13 merged at 6c9d46b; operational evidence commit 18c1188.
  Approved release-job permissions are enabled. Backfill 38909839526 and retry
  38909920867 verified the original 0.1.5 tag/Release/public assets and no-op behavior.
  [Backfill evidence](docs/agent/evidence/XRAY-RELEASE-001-backfill-verified.json).
- **PR:** https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/14 (draft).
- **Scope:** [task](docs/agent/task-release-016.md). One iteration; no parallel release.
- **Candidate:** 0.1.6 was unused. Version literals only in metadata/publisher;
  no runtime, dependency, permission or accepted automation changes. Finalize
  changelog, enabled-workflow instructions and shared README badge documentation.
- **Status:** all five profiles pass: 253 tests + 19 subtests, 32 harness checks,
  offline validation, package/Twine, 14 installed README commands, strict docs/links
  and local desktop/mobile browser. Mypy and changed-file Ruff pass. Six badge
  image URLs/targets and GitHub/PyPI renderer output reverified with normal TLS.
- **Digest:** `e4f37e5a3fe166c5455083334d45a2e109cc038d531552fc433192d503e701df`.
- **Gate:** independent reviewer /root/review_badged_package_release passed head
  850c4c9 and the recorded digest; all six exact-head CI runs passed. Acceptance
  is recorded. Evidence-only acceptance commit CI remains required before merge
  and publication. Existing scoped permission approval remains valid; do not ask
  again. Recheck 0.1.6 availability immediately before publishing.
- **Next:** `python tools/agent.py preflight`; obtain independent review and verify final CI.
- **Limits:** current Pages coverage snapshot is measured 0.1.5 (95.8% lines,
  87.9% branches), not a claim of a new measurement. Live PyPI 0.1.6 badges remain
  pending publication. Live browser certificate failure requires user handoff;
  no bypass, no workplace/private data, no new credentials or access changes.
