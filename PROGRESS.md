# Current handoff

- **Task:** XRAY-HARNESS-001, repository-native harness; owner: Michael.
- **Baseline:** stable 0.1.3 at `8160bec9fb777fc86c28985040f8e4a46253dc6f`.
- **Scope:** [user request / PR body](docs/agent/task.md); [execution ledger](feature_list.json).
- **Implemented:** short agent map, factual module map, stdlib lifecycle/check CLI,
  preserved-runtime/publisher drift checks, source provenance, evidence acceptance rules.
- **Verification:** implementation checks and deliberate failure fixtures are in progress.
  The 115-test released baseline is historical, not proof of this branch.
- **Measured debt:** five pre-existing Ruff errors; existing mypy src/tests baseline passes.
- **Pending:** finish and run lifecycle tests; run package/docs profiles; draft PR CI;
  independent human/fresh-context review. No passing review has been claimed.
- **Limits:** no live Jira validation, no real model-performance benchmark, no custom agent
  runtime, no credential/permission/dependency/runtime/release changes.
- **Next command:** `python tools/agent.py check --profile harness`

Use `python tools/agent.py resume` after reading this file. Local checkpoints and
raw logs live in ignored `.harness/`; checked-in state is the cross-session handoff.
The course and prior implementation are design references, not project authority.
