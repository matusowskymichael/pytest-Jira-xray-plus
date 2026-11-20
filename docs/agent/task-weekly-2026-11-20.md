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
8.5.3-j10, workflow security and release infrastructure. No workplace access/data,
credentials, new permissions, purchases or security-warning bypass. PR42 is
separate and remains untouched. Do not retry previously denied historical artifacts.

Archive the completed ledger with provenance. Prepare a frozen scoped commit and
initial draft PR so the parent can coordinate independent review while all five
current-source harness profiles, installed-wheel guide and exact-head CI run.
Prepare version 0.1.12 on this same draft PR after the parent's initial review of
47ff4d52f11a0f4e79c10a4ab16fed16bebbfdf9. Preserve that runtime and regression-test
diff exactly. Update package metadata, release notes, guide and only required
publisher version literals; preserve all workflow security controls. Verify wheel,
sdist, installed guide, current public version and fresh exact-head checks for a
second independent review. Do not merge, approve, deploy, tag, publish, change
settings or dispatch the release. Keep the candidate explicitly unpublished.
Return exact source, evidence, checks and remaining review/approval gates, then stop.
