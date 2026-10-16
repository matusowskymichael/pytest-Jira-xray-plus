# Version tags and GitHub Releases

A **tag** names the exact source commit for a version, such as `v0.1.5`. A
**GitHub Release** adds that version's changelog notes and downloadable wheel and
source distribution. Installing the package still uses PyPI.

## Status and permission approval

PR #13 passed independent review, received explicit permission approval and was
merged on 2026-10-16. The workflow is enabled. The already-published
0.1.5 came from commit `d007adeefe5057ed9dcbb6ce6c4d28ec7eff942e`, publisher run
`38900871866`; do **not** publish that version again.

The **Tag verified PyPI release** job uses the existing short-lived
`GITHUB_TOKEN` with exactly:

- `actions: read`, to inspect the successful publishing run and download its artifact.
- `contents: write`, to create the version tag, draft Release, upload the two
  verified distribution assets and publish the matching draft.

The user explicitly approved these job-scoped permissions; no further scope is implied.
No token/account is created, no persistent repository access or default permission
is changed, and no `id-token: write` is added. The PyPI publisher and its `pypi`
environment remain unchanged. GitHub's token cannot be restricted to tags/releases
alone: `contents: write` is the actual scope, although this script only performs
the documented release operations. A repository policy that disallows this scope
must be resolved by the maintainer; do not broaden permissions to work around it.

## Normal release

1. Prepare a new, unused stable `X.Y.Z` version. Update `pyproject.toml`, version
   literals in the existing publisher, and the version's dated section in
   `CHANGELOG.rst`. Keep that section headed `X.Y.Z [YYYY-MM-DD]` followed by `=`.
2. Complete tests, independent review and exact-head CI; merge to `main`.
3. In GitHub **Actions → Publish release → Run workflow**, select `main`, enter
   its full reviewed commit SHA, and explicitly select publication. A dry run
   performs validation but does not tag or create a Release.
4. After successful PyPI publication, **Tag verified PyPI release** starts
   automatically. It checks the publishing workflow, branch, repository, successful
   build and publish jobs, source version and notes at that exact commit, artifact
   archive digest, distribution hashes, PyPI metadata and both public downloads.
5. The job creates `vX.Y.Z` at that commit and a draft Release. It uploads the exact
   wheel and sdist from the verified artifact, checks their GitHub hashes, then
   publishes the draft. Visit GitHub **Releases** to inspect the notes and assets.

Immediately before publication, the draft is reread and must still identify the
intended tag, name, notes and non-prerelease state. The returned published release
identity/state and the tag's commit are checked again before success is reported.
A retargeted draft therefore stops before publication; unexpected publication
responses never produce a success claim.

The source is read as data; downloaded source and artifacts are never executed.
The tag is tied to the published commit, even if `main` has advanced. All
GitHub writes happen after the PyPI checks. Failed/cancelled publication cannot
create a tag or Release. The workflow never publishes to PyPI itself.

## Retry an existing publication

The 0.1.5 backfill succeeded in run `38909839526`; a second run `38909920867`
left the tag, Release identity/notes/timestamps and asset identities/hashes unchanged.
Both public GitHub assets matched PyPI bytes.

For a retry or another backfill, select
**Actions → Tag verified PyPI release → Run workflow**, choose `main`, and enter
`38900871866` as `publish_run_id` to recheck 0.1.5 without republishing it. For another version use its
successful **Publish release** run ID, not a test run or the tagging run ID.

A matching completed Release is a no-op. An interrupted upload leaves a matching
draft and tag; retry resumes missing assets, verifies everything again and then
publishes. A tag-only partial attempt can resume. A failure after PyPI success
therefore needs only a tagging retry, **never another PyPI upload**.

Conflicting tags, notes or assets cause failure; nothing is force-moved, deleted,
clobbered or silently rewritten. A published Release missing assets also stops
for manual review. Inspect the conflict before taking any action. Unexpected API
responses, TLS errors, unavailable artifacts, yanked releases or hash mismatches
stop safely. Do not bypass certificate errors.

The existing publisher retains artifacts for **seven days**. Backfill/retry needs
that exact artifact; if it has expired, this automation stops. Do not rebuild a
replacement and claim identical provenance. Review recovery separately. No
automatic backfill of older releases occurs. GitHub may also reject creating an
old tag if its workflow files differ from current main; this implementation does
not request extra Workflows permission or create a token to circumvent that rule.

## Verification limits

Synthetic API tests exercise gating, conflict handling, exact-byte validation,
partial retries and token redaction. They do not prove GitHub grants write access.
The enabled workflow has verified the 0.1.5 tag target, release notes, public asset
hashes and no-op retry. Every later release still needs its own live verification. In the current builder environment,
GitHub artifact storage returned proxy HTTP 403; CI artifact access is a separate
live check. Public PyPI 0.1.5 files and publisher hashes were verified successfully.
Live Pages browser validation is separately blocked by a certificate warning;
normal HTTPS content checks passed. A user must check Pages in a trusted browser.

## Official references checked 2026-10-16

- [GitHub Release API](https://docs.github.com/en/rest/releases/releases): required
  write scope, explicit tag/commit, draft publication and existing-tag behavior.
- [Git references API](https://docs.github.com/en/rest/git/refs): create a reference
  without updating an existing tag.
- [Workflow jobs API](https://docs.github.com/en/rest/actions/workflow-jobs): latest
  build/publish job results, including retry handling.
- [Workflow run events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run):
  completion events and the security boundary of the privileged follow-up workflow.
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/):
  existing OIDC publication remains separate from GitHub release permissions.
