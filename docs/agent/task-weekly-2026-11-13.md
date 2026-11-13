# Reconcile completed-release recovery instructions

One November 13 weekly maintenance iteration. Main 7d416f2 has published 0.1.11
and passed its final CI, but AGENTS still names 0.1.10 and active release work,
while progress and the ledger describe completed checks as pending. Reconcile
those records, archive accepted evidence with exact provenance, and remove static
release/task claims from the entry point so the ledger supplies current scope.
Document an explicit completion/recovery procedure that distinguishes old red
runs and historical handoffs from current main, release and documentation state.

Update the changelog, full beginner guide's contributor instructions and relevant
maintainer/recovery documentation. Preserve all shipped runtime, tests, tools,
dependencies, version, workflow permissions and publication controls. No new
integration or runtime feature, package release or tag. PR42 is separate and must
remain untouched. Generic Tests on on-premises Xray 8.5.3-j10 and all privacy
defaults remain unchanged; no workplace access/data, credentials, purchases,
accounts, permission expansion, destructive cleanup or security-warning bypass.
Do not retry the previously denied historical coverage artifact.

Start a draft PR, run all five current-source profiles and installed guide checks,
obtain independent technical review, then merge only after exact-head CI passes.
Verify merged main and existing Pages deployment using validated HTTPS and local
browser checks. Record observed facts and a stop instruction, not an indefinitely
pending checkpoint or instructions to rerun a completed publisher. Recheck actual
remote head CI at completion; stop after this one iteration. No GitHub approval
action or PyPI publication is part of this repository-only scope.
