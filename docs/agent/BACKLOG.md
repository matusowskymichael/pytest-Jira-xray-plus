# Maintenance audit and prioritized backlog

Audited 2026-10-16 on clean main 3e5f083. Remote main and all three main CI runs
match; no open PRs/issues; public PyPI JSON latest 0.1.6. PR15's independently
reviewed collection lookup optimization is merged but Unreleased. Read current
AGENTS, ledger, progress, architecture/testing/completion and maintainer policy;
no checkout skill files found. No workplace or private data used.

1. **Completed: controlled malformed Test-key collection errors (PR16).**
   xray_plugin.py validates defects inside a caught XrayError path, but key parsing
   in _verify_jira_ids_for_items escapes the collection hook. Reproduce missing,
   empty and wrong-type markers in serial/xdist, then extend the existing safe path.
   This is a user-facing failure-handling gap, ahead of further speed work.
   Reproduced before patch: 20 new cases fail with INTERNALERROR; seven valid/disabled
   compatibility cases pass (see XRAY-PRODUCT-003-before evidence).
2. **Selected: duplicate-policy collection errors.** Existing disallowed duplicate
   keys raised outside the safe collection path on merged PR16. Eight regression
   scenarios reproduce INTERNALERROR/exit 3; five compatibility scenarios pass. Preserve exact diagnostic
   order and grouping; changed exit classification needs explicit regression
   evidence and docs. Separate from malformed-key validation.
3. **Investigate result aggregation lookup cost.** TestExecution.find_test_case
   linearly scans public mutable tests. Unlike collection membership, indexing may
   change behavior after list/key mutation. Benchmark and define compatibility
   before implementation; do not blindly add a cache.
4. **Investigate atomic-report cleanup failures.** Both report writers unlink temp
   files in finally; a permission error could mask the primary error. Reproduce
   synthetically before deciding whether a narrow fix is useful.
5. **Live compatibility validation remains unavailable.** Generic 8.5.3-j10/custom
   Automatic mapping requires an authorized sandbox/user validation. Never access
   the workplace, invent native iteration support, or bypass TLS to advance it.

Privacy audit: scalar parameter values remain opt-in; report identities have an
explicit redaction option; uploads are withheld for incomplete sessions; transport
has timeout/redirect controls. No new privacy defaults or transport changes proposed.
Docs already contain full installed tutorial, migration and troubleshooting. Update
only relevant behavior explanations and keep installed command verification.

Release planning: combine useful accepted Unreleased changes into an independently
reviewed milestone, choose an unused version only at that boundary. Continue useful
work through October 18, 2026 23:59 Asia/Dubai; no quota and no parallel implementation.

API check: pytest's current official collection hook reference requires notifying
`pytest_deselected` when filtering collected items. This fix sends that notification
before clearing the items on malformed marker configuration; regression probes
verify the notification in serial and xdist. Source checked 2026-10-16:
https://docs.pytest.org/en/stable/reference/reference.html#pytest.hookspec.pytest_collection_modifyitems
