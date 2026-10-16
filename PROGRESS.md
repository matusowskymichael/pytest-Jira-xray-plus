# Independently accepted — malformed Test-key validation

- Task XRAY-PRODUCT-003; baseline 3e5f083; PR15 remains Unreleased, PyPI 0.1.6.
- [Draft PR #16](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/16).
- [Prioritized audit](docs/agent/BACKLOG.md); [scope](docs/agent/task-test-key-validation.md).
- Reconciled clean main, current instructions/ledger/progress, no open work, PyPI
  latest 0.1.6 and all prior main checks before selecting this real failure gap.
- Before fix: 20 new malformed-key tests failed with INTERNALERROR, seven valid/
  disabled compatibility checks passed. Durable baseline summary records log hash.
- Runtime fix extends existing guarded collection validation to Test keys and
  notifies pytest_deselected before clearing items, per official hook documentation.
  Does not change duplicate-key policy or valid marker forms. No new key regex.
- 27 new regressions cover malformed shapes, serial/xdist, no fixtures/uploads,
  continue-on-collection-errors, deselection notifications, valid forms/order,
  same-marker deduplication, disabled reporting and collect-only behavior.
  Focused keys/defects/duplicate suite: 70 passed.
- All five profiles pass on source a41558c: 292 tests + 19 subtests, harness,
  offline checks, build/Twine, 14 installed README commands/full metadata rendering,
  strict docs/links and local desktop/mobile browser. Changed-file Ruff and mypy
  (33 files) pass. Full README and Unreleased changelog explain recovery.
- Digest: 582a39b7cce5efe3aa1f031b2d44b66be3cc078ac614e36b38c51fcdd65c3516.
- Independent review /root/review_test_key_errors PASS supplied by parent at
  2026-10-16T19:38:47Z, recorded unchanged. Read-only source/CI evidence review,
  not live Jira validation. All six reviewed-head CI runs passed.
- Next: verify acceptance-head CI, merge PR16, verify main, then implement
  reproduced duplicate-policy collection errors. Group related changes into a
  later reviewed release; no version bump/publication/permission change now.
- Continuous maintenance continues after this review/milestone boundary, one task
  in flight. Next candidate: investigate disallowed duplicate collection errors;
  then benchmark aggregation lookup without breaking public mutable-list semantics.
  Stop at 2026-10-18 23:59 Asia/Dubai (19:59 UTC), or real blocker/exhausted work.
- Limits: synthetic validation only; Generic on-prem Xray 8.5.3-j10/custom Automatic
  mapping remains unverified live; native iterations unsupported. No workplace/private
  data, new access, purchases/accounts, destructive cleanup or security bypass.
