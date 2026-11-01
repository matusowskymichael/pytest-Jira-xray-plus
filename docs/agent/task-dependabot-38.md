# November 1: repair and merge PR38

Reconcile PR38's original bot commit f212e0640dd97ad3331a6af6939c5af4403bd4c9
with main 486242f2c16bb23836e4255c016ad838b064cb2c, preserving bot history and
user-merged PR36/37 action pins. The latter changed the completed October 30
ledger's protected workflows; archive that ledger at its verified 42ff434 commit
and create this explicitly authorized iteration with fresh evidence. Never reuse
stale acceptance or disable checks. Existing main's build setup helper resolves
the prior duplicated setuptools pin; do not reimplement it.

<transcript_evidence>
User, November 1: “https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/38 please rerun all the failed github action jobs here then merge if it all passes”
Assistant: “The reruns have started, but PR #38’s harness has already failed again: it rejects a change to pyproject.toml against its protected-file baseline. The Python tests are still running. I won’t merge while that check is red.”
User, November 1 15:12 UTC: “Can you fix it?”
</transcript_evidence>

Scope: coverage 7.17.0, setuptools 84.2.1, mkdocs-material9.8.0, necessary
ledger/evidence and maintenance documentation. Preserve runtime, Python matrix,
privacy defaults, all checks, workflow permissions, manual publisher controls
and existing artifact-ID/hash smoke. No PyPI release, Pages deployment, unrelated
changes, credentials, account/security settings or GitHub PR approval action.
Obtain independent technical review and all exact-head checks before merging.
Verify merge and post-merge CI, report limitations, then stop. Do not rerun the
already-running old-head attempts merely to repair this deterministic failure.
