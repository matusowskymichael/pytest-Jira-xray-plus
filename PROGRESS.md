# Review pending — 0.1.7 collection-validation release

- Task XRAY-RELEASE-003; [draft PR18](https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/18).
- PR17 acceptance recorded unchanged, merged at bd231e13702fec4153499aa59a9f815f5d74f475;
  tree identical to acceptance commit 1573a6b, remote main and all three main CI verified.
- Candidate 0.1.7 bundles reviewed PR15–17: collection lookup optimization,
  malformed-key collection errors and duplicate-policy collection errors.
  Public PyPI 0.1.6/latest and unused 0.1.7 verified during preparation.
- Runtime/tooling/dependencies/permissions preserved. Package/publisher diff verified
  exactly as 0.1.6-to-0.1.7 literals. Full beginner README, dated changelog, existing
  release-doc regression and release-readiness plan updated.
- Fresh temporary development environment recreated after restart; all five profiles
  pass on source 5967e86: 305 tests + 19 subtests, harness, offline checks, build/Twine,
  all 14 installed README commands/full description rendering, strict docs/links and
  local desktop/mobile browser. Changed-file Ruff and mypy (34 files) pass.
- Six badge images/targets and GitHub-emitted image URLs pass over normal TLS;
  GitHub/PyPI renderer previews pass. Public coverage/status snapshots remain 0.1.6,
  explicitly not a fresh 0.1.7 measurement. No live visual success is claimed.
- Digest: 8ad23e6a8453152edcabc7f0286e12cda71c7fe50aed69d602f6a46a05810a85.
- Next: final evidence-head CI, then fresh parent-arranged independent release review.
  Freeze review head. No merge/publication until acceptance and final gates pass.
  Immediately before publication recheck unused version and exact reviewed main SHA.
- After publication: verify PyPI/publisher/GitHub asset hashes and tag, fresh public
  installation/tutorial, Pages files and actual measured coverage/status provenance.
  Do not bypass browser security warnings or misreport PyPI Client Challenge HTML.
- Continue justified backlog after the reviewed milestone: synthetic cleanup failure
  can mask report write errors; aggregation cache needs public-list compatibility.
  One task in flight; deadline Oct18 2026 23:59 Asia/Dubai. No workplace/private data,
  new permissions/credentials/accounts/purchases or destructive cleanup. Generic
  8.5.3-j10/custom Automatic mapping remains unverified live; native iterations unsupported.
