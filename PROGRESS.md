# Current iteration — defects validation

- **Task:** XRAY-PRODUCT-002; branch `fix/validate-defects-during-collection`.
- **Reconciled baseline:** main 57d43b2; PyPI 0.1.4; no open issues or PRs and no
  active prior task. 0.1.5 was unused when checked. One iteration in flight.
- **Scope:** [task](docs/agent/task-product-002.md), [ledger](feature_list.json).
- **Status:** 31 focused regressions pass. Initial reproduction: 22 malformed-case
  checks failed on the baseline, while eight compatibility checks passed. Fixed
  list shape/element validation and standard collection-failure reporting; an
  intermediate UsageError-only approach failed four xdist checks and was replaced.
  Full profiles, installed examples and independent review are pending.
- **History:** completed 0.1.4 ledger archived in
  [evidence](docs/agent/evidence/XRAY-PRODUCT-001-completed-ledger.json).
- **Next:** `python tools/agent.py check --profile tests`; prepare a focused PR
  for independent review before merge/release. Scheduled rounds resume this work.

**Binding security rule:** never bypass browser certificate/security errors.
Report browser checks blocked and hand off to the user; normally validated HTTPS
checks are separate. Do not repeat the historical 0.1.4 bypass. No workplace data,
accounts/credentials, purchases or permission changes. Standing merge/release
authorization for October 16–18 does not waive review, evidence or safety gates.
