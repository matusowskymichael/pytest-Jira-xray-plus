# Bound duplicate Test-key collection lookup cost

Authorized follow-up to completed 0.1.6 at a18e361: improve the quadratic list
membership lookup in Xray collection validation. No open PRs/issues and public
PyPI latest 0.1.6 were verified before selecting this scoped optimization.

Use set membership while preserving diagnostic order, first-offending-item failure,
repeated marker-key deduplication, allowed duplicate grouping, and validation of
later malformed markers. Add deterministic comparison-count scaling regression
and a reproducible synthetic benchmark with no timing pass/fail threshold.
Update the full beginner README and Unreleased changelog; retain all existing
installed examples, Generic targeting and privacy defaults. Do not bump versions,
change dependencies, workflows, approved permissions, publishing or API semantics.
Run all five harness profiles and exact-head hosted CI. Return exact head/digest
for fresh independent review before merge/release. No parallel implementation,
workplace access, private data, credentials, purchases, accounts, destructive cleanup
or security bypass. Authority ends October 18, 2026 UAE; no release quota.
