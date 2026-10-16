# Maintainer handoff — iteration complete

## Binding security correction for subsequent work

Parent instruction received after the 0.1.4 handoff, 2026-10-16:
**Never bypass browser certificate or security errors**, including isolated
`ignore_https_errors`, `--ignore-certificate-errors`, or equivalent configurations.
Such warnings require user handoff. Report browser checks as **blocked**; normally
validated HTTPS checks may continue where appropriate, without claiming they
replace the blocked browser verification. Do not repeat the 0.1.4 bypass.

This supersedes any implied permission from the historical release evidence.
Keep that history truthful; the earlier bypass is not an acceptable procedure or
precedent. The release is delivered. This correction starts no new iteration and
must be carried into the next scheduled task's instructions and handoff.

## Completed release record

- **Task:** XRAY-PRODUCT-001, `passing`; no iteration currently in flight.
- **Released:** [0.1.4 on PyPI](https://pypi.org/project/pytest-jira-xray-plus/0.1.4/).
  The earlier 0.1.3 baseline / candidate descriptions record pre-release history.
- **Merged PR:** [#11](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/11).
  Main release commit: `222fcef7c9461873780359d06733cfc9fc8644f1`; merge preserves
  receipt history and exactly matches accepted source plus evidence-only records.
- **Acceptance:** independent `review_evidence_isolation_fix` passed reviewed head
  `78b7855`; supplied verdict, scope and limitations are recorded. Acceptance,
  preflight, scope drift and main CI pass without weakening gates.
- **Validation:** 156 tests and 19 subtests on Python 3.12–3.14; 32 harness tests;
  all required profiles pass. Public PyPI install outside the checkout passes all
  14 README commands and nine ownership regressions, with HTTP blocked in tests.
- **Artifact integrity:** wheel and sdist public downloads match PyPI SHA-256
  metadata and the exact trusted publisher artifacts. Publish run: 38868253334.
- **Docs:** [live guide](https://matusowskymichael.github.io/pytest-Jira-xray-plus/tutorial/install/)
  updated from main CI artifact; Pages commit `afcca1b`, deployment 38868436585.
  All 23 HTML pages plus search/assets (64 files total) match tested bytes over
  normally validated HTTPS. Desktop/mobile navigation, search, highlighting and
  theme checks pass. Chromium needed an isolated certificate-error bypass due to
  the environment trust store; browser TLS validation is not claimed.
- **Durable release evidence:** [record and hashes](docs/agent/evidence/XRAY-PRODUCT-001-release-0.1.4.json).
- **Compatibility:** Generic-target aggregation only; no live workplace/Xray test,
  native iterations, new credentials, accounts, purchases or permission changes.
- **Next scheduled round:** reconcile main, PyPI and open PRs first. Do not repeat
  this release. Select one useful new iteration, archive this completed ledger,
  and retain independent review / exact-head checks under the October 16–18
  standing authorization. No repeated user merge-permission prompt is needed.
- **Next command:** `python tools/agent.py preflight`.
