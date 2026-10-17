# Review pending — authentication configuration errors

- PR19 independently accepted, merged at 3f144256ca910e37a64fb0542c16d6d7faa685f7 with identical accepted tree. Acceptance-head six workflows and main CI 39003343509/39003343499/39003343482 passed. Accepted ledger/review retained and archived.
- Task XRAY-PRODUCT-006: no open issues returned; code investigation reproduced missing auth configuration as INTERNALERROR/exit 3. Draft matrix on unchanged code: 22 expected failures, three offline/collection cases pass. Baseline excerpt/hash retained.
- Focused plugin configuration boundary converts existing auth helper XrayError to pytest.UsageError; no helper/HTTP/selection/TLS/version/workflow changes.
- PR20: https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/20. Full beginner README/auth/troubleshooting/migration and Unreleased changelog updated. Added 25 synthetic regressions; all pass.
- All five profiles passed on b80af58fe55bc9017106746ecb44f9564ca710c9: 353 tests + 19 subtests, 32 harness tests, offline checks, build/Twine, all 14 installed README commands/full metadata rendering, strict docs (23 HTML pages, 1207 references), local desktop/mobile/search/theme checks. Changed-file Ruff and mypy (36 files) pass.
- Digest: 34aaea7a71b23a9cefc44a72cabb89d4d24a2e93c1be83f27c6955a8c0bb10ac.
- Connection checked at 2026-10-17 04:44:45 UTC after parent notification: shell/GitHub healthy, PR19 merge and PR20 pushed head confirmed; no duplicate actions.
- Next: final evidence-head CI, then fresh parent-arranged independent review. Freeze head. No merge before acceptance; no release for version count. Existing browser certificate/PyPI HTML challenge limits remain.
- Published version remains 0.1.7. No workplace/private data or security bypass; live Generic 8.5.3-j10/custom Automatic mapping unverified, native iterations unsupported. One task at a time through 2026-10-18 23:59 Asia/Dubai.
