# Review pending — report path configuration errors

- PR20 independently accepted and merged at 0d3c5f0086771eccb898f8b509839c4f725778a3; tree identical to acceptance commit b6116b8. Six acceptance-head workflows and main CI 39004455946/39004455979/39004455999 passed. Accepted ledger archived.
- XRAY-PRODUCT-007: no open issues returned. Synthetic unresolved home paths, Python 3.12 symlink loops and injected resolution failures reproduce internal configuration errors. Initial 28-case matrix: 21 expected failures, seven passes; two additional preservation cases pass before edits.
- Focused plugin normalization boundary maps only OSError/RuntimeError to option-specific UsageError. Non-strict resolution and writer boundaries unchanged; Python 3.13+ symlink loops may still fail later during writing.
- PR21: https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/21. Full beginner README, troubleshooting/migration, Unreleased changelog and readiness updated. Thirty new regressions pass, including collect-only and unexpected-exception preservation.
- All five profiles passed on 860ffd94cc1936c801d2680e68d2747bf851227a: 383 tests + 19 subtests, 32 harness tests, offline assertions, build/Twine, all 14 installed README commands/full metadata, strict docs with 23 HTML pages/1207 references and local desktop/mobile/search/highlighting/theme. Changed-file Ruff and mypy (37 files) pass. Receipt log hashes verified.
- Digest: dd4aad7934f1036833a7cb0d732e652e32de1ec981786321c43d06b98dbea630.
- Connection checked after parent notification: shell/GitHub healthy at 04:55:54 UTC; PR20 subsequently merged at 04:56:52 UTC. No duplicate actions.
- Next: final evidence-head CI, then fresh parent-arranged independent review. Freeze candidate. No merge before acceptance; no version bump/publication. Existing browser certificate/PyPI HTML challenge limits remain.
- No workplace/private data, new credentials/permissions or browser bypass. Live Xray/custom Automatic mapping unverified, native iterations unsupported. Continue one iteration at a time through 2026-10-18 23:59 Asia/Dubai.
