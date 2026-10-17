# Review pending — report cleanup failures

- [PR19](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/19), task XRAY-PRODUCT-005.
- Verified 0.1.7 release: PR18 merged at 98b56da; publisher 39001854186, GitHub release 39002033257 and Pages 39002185623 passed. Public artifact hashes/tag, fresh PyPI installation/all 14 commands and 101 deployed files verified.
- Release proof commit c8c38b6d4ef095d7738af0b3f1bfec478d1f1594 matches remote main; CI 39002244182/39002244150/39002244132 passed. Archived accepted release ledger and retained release evidence.
- Synthetic replacement plus cleanup failures reproduced raw cleanup exceptions masking primary failures in both writers. Initial nine regression cases: four failed as expected, five passed on unchanged 0.1.7. Baseline log retained with trailing whitespace normalized only.
- Focused two-writer fix preserves error boundaries and original diagnostics, identifies failed cleanup paths, and skips unlink after successful replacement. Unexpected exceptions retain their identity; owned cleanup is still attempted. No payload/version/workflow/dependency changes.
- Added 23 synthetic regressions for both writers, write/close/create/replace failures, cleanup failures, successful replacement, warnings-as-errors, interruptions and subprocess reporting boundaries. Full beginner README, troubleshooting, Unreleased changelog and readiness updated.
- All five profiles passed on source 61486e91e3517ed13658add4be75aafcae640f93: 328 tests + 19 subtests, all 14 installed tutorial commands/full metadata rendering, offline checks, build/Twine, harness, strict docs with 23 HTML pages/1207 internal references and local desktop/mobile/search/theme checks. Changed-file Ruff and mypy (35 files) pass.
- Digest: 55254d10f7b8fcc8dfcd88b433a2f6522dee37b71e5405a222adf9e22025f5b0.
- Next: final evidence-head hosted CI, then parent-arranged fresh independent review. Freeze head; no merge/release before acceptance and final gates.
- No workplace/private data, new credentials/permissions or browser security bypass. Live visual certificate-warning handoff and PyPI HTML Client Challenge remain; local rendering is not live visual proof. Generic on-prem 8.5.3-j10/custom Automatic mapping remains unverified live; native iterations unsupported. Continue one task at a time through 2026-10-18 23:59 Asia/Dubai.
