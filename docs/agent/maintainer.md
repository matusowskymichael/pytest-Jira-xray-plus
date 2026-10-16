# Standing maintainer authorization

Scope: **matusowskymichael/pytest-Jira-xray-plus only**, for the user-requested
three-day maintenance window beginning 2026-10-16. No policy here grants authority
in another repository or changes GitHub permissions/protection.

Michael requested improvements throughout the day, aiming for two or three releases
per day when useful, with documentation and usage updated each iteration. He added:
"And no need to ask me for permission to merge either. Just do it. You can remove
the 'require permission to merge' check in this repo specifically."

This is standing authorization, not a release quota or exemption from review:

1. Resume the current ledger/branch/PR if an iteration is in flight. Scheduled
   rounds must not duplicate it. The parent orchestration owns scheduling.
2. Reproduce a concrete problem; make a focused fix and update documentation.
3. Run required profiles, inspect receipts, and verify CI on the exact candidate.
4. Obtain independent review before merge/release. Builder-authored approval is
   forbidden. Record the review's identity, source, revision, scope and limitations.
5. After acceptance, merge preserving historical evidence commits. No repeated
   user merge-approval prompt is required during this window.
6. Recheck main and choose a still-unused stable version; publish only using the
   existing manual publish.yml, reviewed SHA, exact artifact hashes and pypi
   environment. Use the existing Pages workflow. Do not alter trusted-publisher
   permissions, branch protection or account access. Failed gates block release.

Never access the workplace server or private data, create accounts/credentials,
make purchases, or expand permissions. Keep Generic targeting and documented
compatibility limits; local checks do not prove live Xray behavior or native
iteration support. A useful unreleased candidate is preferable to a forced release.

Historical harness acceptance: main commit
`a0d92ec86e88f3f82914f7e58d9dd501d123d564`; archived ledger:
[evidence/XRAY-HARNESS-001-completed-ledger.json](evidence/XRAY-HARNESS-001-completed-ledger.json).
Its preservation map described that completed tooling task; the active product
ledger now names the authorized runtime change and protects unrelated files.
