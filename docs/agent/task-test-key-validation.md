# Report malformed Test-key markers as controlled collection failures

Continuous maintenance authorized through 2026-10-18 23:59 Asia/Dubai, with one
implementation/release in flight and independent review before merge/publication.
Baseline reconciled: clean main 3e5f083, PR15 merged and Unreleased, public PyPI
0.1.6, no open issues or PRs. Follow the prioritized audit backlog.

Extend the existing early defects-validation collection path to malformed Xray
Test-key markers. Preserve accepted marker forms, same-marker deduplication,
ordering, duplicate-key policy, grouping and privacy opt-ins. When Xray is enabled,
malformed keys must produce a collection error before fixtures/tests/uploads, even
with xdist or continue-on-collection-errors, rather than INTERNALERROR/worker crash.
Notify pytest_deselected before clearing collected items, per the official hook
contract, and verify other plugins receive the notification.
Keep reporting-disabled and collect-only behavior. Add synthetic regression tests,
full beginner usage/troubleshooting and Unreleased changelog; run all five profiles,
installed tutorial commands and exact-head CI. Record evidence and return exact
head/digest for parent-arranged independent review. No version bump in this PR.

Keep Jira plus Xray requirements, existing Generic Tests on on-prem 8.5.3-j10;
no native iterations or live workplace compatibility claims. No workplace/private
data, new credentials/accounts/purchases/permissions, destructive cleanup, or
browser security bypass. Continue the next justified backlog item after review
and milestone completion, within the authorization deadline; do not force releases.
