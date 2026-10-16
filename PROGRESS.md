# Current handoff

- **Task:** XRAY-HARNESS-001, repository-native harness; owner: Michael.
- **Baseline:** stable 0.1.3 at `8160bec9fb777fc86c28985040f8e4a46253dc6f`.
- **Draft PR:** [#10](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/10).
- **Scope:** [request / PR body](docs/agent/task.md); [execution ledger](feature_list.json).
- **Implemented:** short agent map, module boundaries, stdlib lifecycle/check CLI,
  protected-runtime/publisher drift checks, scope provenance and evidence acceptance.
- **Local verification:** 143 tests and 3 subtests pass, including 28 harness tests;
  offline checks pass; fresh-wheel installation executes all 14 README commands with
  HTTP blocked; Twine passes; strict docs build, 23 HTML pages / 1191 internal links,
  desktop/mobile/search/highlighting/theme checks pass. Receipts and logs are in
  [evidence](docs/agent/evidence), bound to content digest
  `2f12089cb95d95ec2ccb54bcc550477f068d351e7c4e5e10c2f66cff018f23c4`.
- **Static checks:** new files pass Ruff; mypy passes for 26 src/test files.
  Five pre-existing broad Ruff issues remain documented in the testing guide.
- **CI:** fix commit `093dc64367850642c568098f3aa692303f2e0afc` passed harness,
  documentation and Python 3.12/3.13/3.14 tests, on push and PR runs.
  Verify the final evidence/handoff commit's checks on the draft PR before acceptance.
- **Failure history:** initial `48c1fd3` run
  [38853027541](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/runs/38853027541)
  failed because the remote-drift fixture omitted `import json`; the downloaded
  artifact confirms that traceback. Fixed in `093dc64`. The other two annotations
  concern Node 20 / Ubuntu runner migrations; they are not this test failure.
- **Pending:** real independent human/fresh-context review. State is `review_pending`,
  never passing; no passing review has been fabricated.
- **Limits:** no live Jira validation, real model-performance benchmark, exhaustive
  course/exercise audit, new runtime, credential/permission/dependency/release changes.
- **Next command:** `python tools/agent.py preflight`, then inspect PR checks and review
  [scope](docs/agent/task.md), diff and evidence using [completion](docs/agent/completion.md).

Use `python tools/agent.py resume` after reading this file. Local checkpoints and
working logs live in ignored `.harness/`; checked-in progress is the cross-session
handoff. Do not merge, publish or deploy as part of this task.
