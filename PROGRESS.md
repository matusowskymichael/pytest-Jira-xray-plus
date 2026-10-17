# Independently accepted — duplicate-key policy collection errors

- Task XRAY-PRODUCT-004; [draft PR17](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/17).
- Baseline main 0d4d05f: PR16 independently accepted and merged; tree matches
  acceptance commit, final remote SHA and all three main CI runs verified.
  [Merge evidence](docs/agent/evidence/XRAY-PRODUCT-003-merged.json).
- PR15 optimization and PR16 fixes remain Unreleased; PyPI is unchanged at 0.1.6.
- Before: eight duplicate-policy regressions failed with internal error/exit 3;
  five compatibility cases passed. No unsafe upload/fixtures observed.
- Fix extends guarded collection validation to duplicate-policy errors while
  retaining exact message/order and first-offending-item behavior. Collection
  errors intentionally replace internal-error classification; README documents
  nonzero exits (serial usually 2, xdist/continue usually 1) and safe recovery.
- 13 new regressions cover serial/xdist × preview/upload × continue, no execution/
  upload, deselection notifications, empty preview, opt-in grouping, disabled
  reporting and collect-only. Focused collection/plugin suites: 104 passed.
- All five profiles pass on source 046361c: 305 tests + 19 subtests, harness,
  offline checks, build/Twine, 14 installed README commands/full description,
  strict docs/links and local desktop/mobile browser. Changed-file Ruff and mypy
  (34 files) pass. No version/dependency/workflow/permission change.
- Digest: 51ac24165a6cfd2f539b1a1ae676a12bb0569f62c5e893233ba47347ef99871e.
- Independent acceptance supplied by /root/review_duplicate_collection_errors,
  bound to head 11a39fc and recorded unchanged with assessment/CI/limits.
- Next: verify acceptance-head CI, merge and verify main CI. Group this with PR15/16 into the next coherent reviewed stable milestone;
  do not publish each tiny change separately. One task in flight.
- Then continue justified backlog: aggregation lookup is quadratic but public-list
  mutation/first-match compatibility needs careful design and tests. Do not add
  an invalid cache. Authority ends Oct18 2026 at 23:59 Asia/Dubai.
- Limits: synthetic tests only; Generic on-prem 8.5.3-j10/custom Automatic mapping
  unverified live; no native iterations/workplace/private data/security bypass.
