# Current maintainer iteration

- **Active task:** XRAY-PRODUCT-001, isolate attachments/defects between mapped Test keys.
- **Candidate PR:** [#11](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/11).
- **Branch:** `fix/isolated-test-key-attachments`; one iteration in flight. Scheduled
  rounds must resume this task and its PR, not create a duplicate.
- **Baseline:** main `a0d92ec86e88f3f82914f7e58d9dd501d123d564`; published 0.1.3.
- **Candidate:** 0.1.4, unpublished; public PyPI JSON reported this version unused.
- **Reproduction:** eight of nine new ownership regressions failed before the fix.
  The mixed-mapping reverse serial order passed, demonstrating order sensitivity.
- **Fix:** copy incoming evidence/defect list containers per TestCase. Preserve
  identical attachment occurrences, defect de-duplication, statuses and comments.
- **Current verification:** targeted regressions pass; full profiles and exact-head
  CI are pending. Runtime change is limited to helper.py. Publisher changes are
  version literals only; access and publishing safeguards remain intact.
- **Scope:** [current task](docs/agent/task-product-001.md), [ledger](feature_list.json),
  [standing maintainer authorization](docs/agent/maintainer.md).
- **History:** the accepted harness ledger is archived in
  [evidence](docs/agent/evidence/XRAY-HARNESS-001-completed-ledger.json); old proof
  is not claimed valid for the new source. New independent review is required.
- **Next command:** `python tools/agent.py check --profile tests`.

Prepare the candidate for independent review before merge or release. During the
standing window, accepted iterations need no repeated user merge-permission prompt.
No workplace data/server access, new credentials/accounts, purchases, permissions
or branch-protection changes. Native iterations and live server behavior remain
unverified. No merge, PyPI publication or Pages deployment has occurred this iteration.
