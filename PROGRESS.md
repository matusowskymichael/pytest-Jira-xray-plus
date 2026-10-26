# October 26 — Dependabot PR #32 repair in progress

Current main reconciled; prior accepted ledger archived. Fresh scoped evidence and
independent review required before this PR merges. No release authorized by this
task. Other updates remain separate.

# October 23 weekly iteration completed — published 0.1.10

PR [#30](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/30) merged
as `6867988a123e019cda2bc383c8f73b63c53f34d6` after external independent review
and six acceptance-head CI checks. All three main CI workflows passed. Existing
trusted publisher [39921970054](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/runs/39921970054)
and automatic tag/release [39922389468](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/runs/39922389468)
succeeded. [PyPI 0.1.10](https://pypi.org/project/pytest-jira-xray-plus/0.1.10/) and
[GitHub v0.1.10](https://github.com/matusowskymichael/pytest-Jira-xray-plus/releases/tag/v0.1.10)
are public; tag points to the exact released source.

The meaningful fix rejects explicit empty report paths before collection,
authentication or publisher selection. Full beginner guide and migration explain
this correction. Public wheel/sdist hashes match PyPI, publisher log and GitHub
assets; full README metadata matches. A fresh public PyPI install passed all 15
guide commands and six serial/xdist empty-path probes outside the checkout, with
HTTP blocked. Candidate tests: 562 passed plus 19 subtests; all five profiles and
independent review passed. Clean release-source coverage: 771/787 lines (98.0%),
231/252 branches (91.7%); all 562 tests plus 19 subtests passed under coverage.

[Live quick start](https://matusowskymichael.github.io/pytest-Jira-xray-plus/tutorial/install/)
is deployed at Pages commit `01de9a394a90a1a3cecda4d034e1371faf81d991`, deployment
[39922506846](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/runs/39922506846).
All 102 live files match checked build bytes over normally validated HTTPS.
Local checks cover 41 HTML pages/2917 references plus desktop/mobile/search/theme.
Hosted Chromium remains blocked by ERR_CERT_AUTHORITY_INVALID for Pages and PyPI;
no certificate bypass was used. Live Jira/Xray, custom Automatic mapping and
native iterations are not validated; native iterations remain unsupported.

[Complete release evidence](docs/agent/evidence/XRAY-WEEKLY-001-release-completion.json)
links all receipts and hashes. Final operational record changes only progress and
evidence; its own exact-head CI is the remaining bookkeeping check. Bot PR32-35
remain separate/unmodified. No credentials, permissions, dependency upgrades or
workplace access. Stop after this one weekly iteration; no next implementation or
release is authorized by this iteration. Earlier candidate checkpoints below are
historical, not current publication state.

---

# October 23 weekly iteration — independently accepted 0.1.10 candidate

- Fresh main 6ee20aa3a59e08f7b80c6e312f9758a3876c642a: Dependabot setup completed, both initial jobs successful; prior main progress was stale. Archived accepted main ledger and paused PR30 ledger. Merge resolves maintenance-record conflicts without dropping either history.
- No open issues. PR30 was draft/conflicting, old CI green. Resume the existing draft; do not create a duplicate. Bot PR32-34 have red harness checks; new bot PR35 changes setuptools and has red tests/harness. All remain separate/unmerged. Published PyPI latest 0.1.9; 0.1.10 unused at preflight.
- Meaningful fix: explicit empty --xraypath currently selects upload. Preserve existing two-line guard and 37 regressions; no broader runtime/dependency changes. Prepare 0.1.10 metadata and manual publisher version literals only; full README/changelog/migration and source checker documentation updated.
- Fresh verification and independent review required before merge/release. No workplace/private data, new credentials/permissions or security bypass. Generic on-prem Xray8.5.3-j10 targeting retained; native iterations unsupported. One weekly iteration only, stop afterward.

- Fresh checks passed at d20dc861b6a525dd92cac5e2f182724495764b69, digest 2f73ae83596396a880c84119902b05e7e09de3b9e08c7bef62dfcc2a6c93ab1f: 562 tests plus 19 subtests, all five profiles, all 15 installed guide commands/full metadata, 23-page docs check/local browser, 38 focused regression/rendering tests, six candidate-wheel empty-path probes outside checkout. All 13 profile log hashes verified. Changed-file Ruff, mypy (43 files), version-only publisher/metadata comparisons and non-evidence whitespace checks passed. Historical immutable failure logs retain original whitespace.
- Normal-TLS public tutorial/compatibility/status checks pass for currently deployed 0.1.9. Hosted Chromium tutorial and PyPI both remain blocked by ERR_CERT_AUTHORITY_INVALID, without bypass. Candidate site/release is not yet published. Next: exact frozen-head CI and fresh independent review; later main CI, existing publisher, exact public artifacts/install, measured coverage and Pages verification remain operational release gates.

- External native reviewer /root/review_pytest_release_candidate approved exact head 3b5782a5bed21e37ceca244d99e293e60a43fbde with no findings, verifying all 13 profile log hashes and reading 37 regressions. No self-review; limitations recorded. All six reviewed-head CI workflows passed; harness acceptance passed. Next: acceptance-head CI, merge, main CI, unused-version recheck, existing trusted publisher and public verification. No publication claimed yet.
