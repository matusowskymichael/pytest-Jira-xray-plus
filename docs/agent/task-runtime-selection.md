# Validate only selected Xray tests before execution

One user-requested plugin runtime maintenance iteration following completed PR40.
Current released 0.1.10 validates Xray markers before pytest applies -k/-m filters.
Selecting one parametrized case can therefore fail with duplicated keys from
cases that will not run. Run marker and duplicate validation after standard
selection, still before fixtures, preserving failures for selected invalid markers
or duplicate keys. Use supported pytest hook ordering; do not change status,
authentication, payload aggregation, privacy or network behavior.

Reproduce failures before the fix; cover -k/-m and serial/xdist, malformed
excluded markers and selected duplicate controls. Bump the patch version to
0.1.11 if available; update changelog, full beginner guide, migration and applicable
docs. Archive the completed ledger with accepted provenance. Require fresh five
profiles, installed guide and wheel selection probes, independent technical
review and exact-head CI. Start draft PR, merge accepted source, verify main CI.
No GitHub approval action, new integration, workplace access, credentials,
permission changes, purchases or security-warning bypass. Generic Tests on
on-premises Xray8.5.3-j10 remain the target; no live-server/native-iteration claim.

Standing release authorization was explicitly confirmed in this thread: release
meaningful verified runtime changes through existing manual trusted publishing
only. Verify unused version, exact reviewed SHA, public artifacts and hashes,
clean installed guide and regression, tag/release and deployed Pages. No workflow
permission changes. Stop after this one iteration; do not resume continuous work.
