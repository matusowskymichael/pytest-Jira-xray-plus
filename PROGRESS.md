# Current iteration — defects validation

- **Task:** XRAY-PRODUCT-002; branch `fix/validate-defects-during-collection`.
- **Reconciled baseline:** main 57d43b2; PyPI 0.1.4; no open issues or PRs and no
  active prior task. 0.1.5 was unused when checked. One iteration in flight.
- **PR:** https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/12 (draft).
- **Scope:** [task](docs/agent/task-product-002.md), [ledger](feature_list.json).
- **Status:** 31 focused regressions pass. Initial reproduction: 22 malformed-case
  checks failed on the baseline, while eight compatibility checks passed. Fixed
  list shape/element validation and standard collection-failure reporting; an
  intermediate UsageError-only approach failed four xdist checks and was replaced.
  All five profiles pass on digest
  `76241e52190551b452db0807f64bf505baa156888ee49dc1f1bcfa9d1435d493`:
  187 tests + 19 subtests, 32 harness checks, offline aggregation, package/Twine,
  all 14 installed README commands, strict docs/links and local desktop/mobile
  Chromium. An additional run outside the checkout against the installed 0.1.5
  wheel passes all 31 new regressions. Ruff on changed Python and mypy also pass.
  Exact-head hosted CI passed. Independent reviewer `/root/review_defects_validation`
  passed the reviewed head/digest; the parent conveyed acceptance and release authorization.
  Acceptance is recorded; release verification is in progress.
- **Compatibility:** valid defect strings are preserved without key-format rules.
  Reporting disabled and `--collect-only` retain their existing behavior; collect-only
  does not validate Xray markers. No live Xray or native-iteration proof is claimed.
- **History:** completed 0.1.4 ledger archived in
  [evidence](docs/agent/evidence/XRAY-PRODUCT-001-completed-ledger.json).
- **Next:** `python tools/agent.py preflight`; check hosted CI on the final head,
  then merge the accepted candidate and use the existing publisher for unused 0.1.5.
  Scheduled rounds resume this work.

**Binding security rule:** never bypass browser certificate/security errors.
Report browser checks blocked and hand off to the user; normally validated HTTPS
checks are separate. Do not repeat the historical 0.1.4 bypass. No workplace data,
accounts/credentials, purchases or permission changes. Standing merge/release
authorization for October 16–18 does not waive review, evidence or safety gates.
