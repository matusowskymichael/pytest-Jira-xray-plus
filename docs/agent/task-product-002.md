# Validate malformed defects markers before test execution

Authorized October 16–18 maintainer iteration for pytest-Jira-xray-plus only.
Reconcile main, releases and open work before starting; one iteration in flight.
Baseline is published 0.1.4 and main 57d43b2, with the browser security correction.

Confirm malformed xray defects markers currently fail late or produce malformed
payloads. Add narrow collection-time validation only when Jira/Xray reporting is
enabled. Preserve valid lists, including empty lists, original string values and
existing aggregation semantics. Do not introduce speculative Jira-key regex rules.
Invalid marker configuration must prevent fixture execution and upload, and errors
must not expose marker values or call arbitrary repr. Cover serial and xdist,
preview and upload paths with synthetic fixtures and blocked transport, plus
reporting-disabled behavior. Update beginner README, usage docs and changelog.

Prepare unused 0.1.5 and update only version literals in the existing publisher.
Preserve dependencies, unrelated runtime, CI/access permissions and trusted setup.
Archive the completed iteration's ledger without transferring its passing claim.
Fresh checks, installed examples, exact-head CI and independent review are required
before acceptance or merge. Return the review-ready head/digest to the parent;
do not publish during candidate preparation. Standing authorization removes
repeated merge-permission prompts after independent acceptance, not safety gates.

Never bypass browser certificate/security errors. Such warnings block browser
checks and require user handoff; normally validated HTTPS checks are separate.
No workplace access/data, credentials/accounts, purchases or access expansion.
