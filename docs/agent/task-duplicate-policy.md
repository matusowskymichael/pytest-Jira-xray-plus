# Report duplicate-key policy violations as controlled collection errors

Continue from reviewed/merged PR16, main 0d4d05f with all main checks green.
Read-only investigation reproduced disallowed duplicate Test keys causing exit 3
and INTERNALERROR in serial/xdist and preview/upload modes; xdist also showed a
controller KeyError. No fixtures or unsafe upload were observed.

Extend guarded collection validation to duplicate-policy violations. Preserve
exact duplicate diagnostic, order and first offending item, same-marker key
deduplication, allowed duplicate grouping, valid key forms and disabled/collect-only
behavior. With Xray enabled, disallowed duplicate keys must fail collection without
internal/worker errors, fixtures/tests/uploads, even with continue-on-collection-errors.
Notify deselection, preserve offline diagnostic previews and nonzero error exits.
Document intentional change from internal-error exit 3 to pytest collection-error
classification; update existing regression expectation, add focused serial/xdist
and grouping/privacy regressions, full beginner usage/troubleshooting and changelog.
Run five profiles, installed examples and exact-head CI; parent arranges independent
review before merge. Keep one implementation in flight. No version bump now: group
related accepted collection fixes with PR15 into a later coherent reviewed release.

No dependency/workflow/permission expansion, workplace access/private data, new
credentials/accounts/purchases, destructive cleanup or security bypass. Jira and
Xray remain required, existing Generic target on-prem 8.5.3-j10; no native iterations
or live compatibility claims. Continue justified backlog work through Oct18 2026
23:59 Asia/Dubai only, respecting each review/release boundary.
