# Correct misleading offline export failure messages

One November 20 maintenance candidate, based on main
7511b29d5150b1a8e516594835bc094bda5d0f02 and published 0.1.11. Reproduce
with a clean installed public wheel: a directory destination for --xraypath
fails locally but the terminal summary says Jira publishing failed. Correct only
the offline FilePublisher failure heading and summary. Keep the underlying error,
exit codes, atomic writer cleanup and online behavior unchanged. Exercise passing
and failing tests, directory and invalid-parent paths, serial and xdist runs,
successful export and existing online failure controls with synthetic inputs.

Update changelog, relevant documentation and the full beginner guide. Preserve
runtime dependencies, authentication, privacy, Generic Tests on on-premises Xray
8.5.3-j10, workflows and release infrastructure. No workplace access/data,
credentials, new permissions, purchases or security-warning bypass. PR42 is
separate and remains untouched. Do not retry previously denied historical artifacts.

Archive the completed ledger with provenance. Prepare a frozen scoped commit and
initial draft PR so the parent can coordinate independent review while all five
current-source harness profiles, installed-wheel guide and exact-head CI run.
Do not merge, approve, deploy, tag or publish. Package-version/release preparation
remains for the parent's subsequent coordinated release decision; identify this
candidate as unreleased and preserve current 0.1.11 metadata/publisher pins here.
Return exact source, evidence, checks and remaining review/approval gates, then stop.
