# October 23 weekly maintenance: complete PR30 and prepare 0.1.10

Resume existing draft PR30 rather than duplicate work. Fresh main is 6ee20aa,
Dependabot setup is merged and its two first jobs succeeded; published PyPI latest
is 0.1.9 and 0.1.10 is unused at preflight. No open issues. Bot PRs32-34 are major
Actions upgrades with failing harness checks; PR35 changes setuptools and has
failing tests/harness. Leave these upgrades unmerged and separate from this task.
Reconcile main into PR30 preserving both histories, existing Dependabot settings,
weekly policy, documentation and evidence; retire stale pause/pre-merge progress.

Complete the existing two-line empty-report-path guard: explicit empty strings for
--xraypath, --xray-case-report and --xray-full-report are usage errors (exit 4)
before collection/fixtures/worker startup/authentication/transport. Omitted flags,
collect-only, nonempty paths including spaces, expansion/collision rules, privacy,
Generic aggregation, reruns/phases and valid uploads/exports retain their behavior.
This fixes an actual unwanted upload selection when an offline filename is empty;
it is a meaningful package correction warranting 0.1.10 after verification.

Keep the 37 regression tests and all existing runtime/tests/tools unchanged except
the existing plugin guard. Prepare version 0.1.10 in package metadata and only
version literals in the existing manual publish.yml. No dependency upgrades,
permissions or publisher-policy changes. Update full beginner guide, changelog,
maintainer docs and release readiness with safe nonempty filename examples,
0.1.9 workaround and migration guidance; preserve fifteen installed commands.

Run all five profiles, focused regressions, installed candidate empty-path probes,
metadata/rendering and local/public docs checks, changed static checks, publisher
version-only comparison and exact-head CI. Obtain fresh parent-arranged independent
review before acceptance/merge/release. After main CI, recheck unused version and
publish only through existing manual trusted pypi environment with reviewed SHA;
verify exact public artifacts/tag, public installed guide, refresh measured
coverage/status and existing Pages, verify normal-TLS live files. Report browser
certificate failures without bypass. No workplace or private data, credentials,
accounts, purchases, destructive cleanup or permission expansion. Live Xray
8.5.3-j10 remains unverified; native iterations/datasets unsupported.

Stop after this one weekly iteration. Do not start the next bug or dependency PR.

User, October 23 scheduled task: "Existing authorization covers scoped tested and independently reviewed commits/PRs, merging accepted maintenance, GitHub Pages updates and stable PyPI releases through existing trusted publishing. Release only when meaningful verified package changes warrant it; repository-only fixes do not require a PyPI release."
User: "This replaces the former continuous effort and daily release quota; do not continue automatically from one iteration to the next between scheduled runs."
