# Independently accepted — collection lookup

- Task XRAY-PERF-001; branch perf/collection-key-lookup; baseline a18e361 (0.1.6).
- [PR #15](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/15).
- Reconciled main instructions, completed ledger/progress, no checkout skills,
  no open PRs/issues and latest public PyPI 0.1.6 before choosing this scoped task.
- Two-line runtime change uses a set for membership only; diagnostic list/order,
  first-offending-item behavior, validation and report grouping remain unchanged.
- Before patch: six deterministic scaling tests failed, six behavior tests passed.
  At 512 unique keys, old list lookup needed 130,816 equality comparisons.
  [Before log](docs/agent/evidence/XRAY-PERF-001-before.log).
- After patch: all 12 new tests pass, including serial/xdist output. Synthetic
  benchmark at 1,024 unique keys: baseline 523,776 equality comparisons versus
  candidate 0 equalities/3,072 hash calls in both duplicate modes. Deliberately
  distinct hashes isolate lookup growth; no timing threshold or end-to-end claim.
  [Benchmark](docs/agent/evidence/XRAY-PERF-001-benchmark.json).
- All five profiles pass on source 8730f0e: 265 tests + 19 subtests, harness,
  offline validation, package/Twine, all 14 installed README commands and full
  README rendering, strict docs/link checks and local desktop/mobile browser.
  Changed-file Ruff and mypy (32 files) pass. Full README/changelog updated.
- Digest: 847466450908b5d2f2b32f206ddcc276b02e207993054dea0b47acde055d7ee8.
- Independent reviewer /root/review_duplicate_lookup_optimization passed exact
  head 7e2f468 and digest; all six exact-head CI runs passed. Review recorded in
  [acceptance evidence](docs/agent/evidence/XRAY-PERF-001-independent-review.json).
- Next: verify acceptance-commit CI, merge PR #15, then verify main CI. Keep under
  Unreleased and PyPI 0.1.6 unchanged; no publication or permission change.
  Existing authorization ends Oct 18 UAE.
- Limits: synthetic validation only; Generic on-prem Xray 8.5.3-j10/custom Automatic
  live mapping unverified; native iterations unsupported. No workplace/private data,
  credentials, purchases, accounts, destructive cleanup or security bypass.
