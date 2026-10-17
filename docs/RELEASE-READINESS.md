# Stable 0.1.0 release decision — 2026-10-15

Michael reported successful validation and explicitly authorized publishing the
current feature set as stable 0.1.0. This is **user-reported successful use**, not
independently observed exhaustive validation. No private test content, credentials,
hostnames or issue keys were requested or recorded.

The product integrates pytest with Jira and Xray. Its implementation includes case/attempt audit reports and
aggregate Xray comment fallback, including bounded comments/full archival,
conservative retry summaries, transport failure handling and partial-upload
suppression. The 0.1.0 release changes metadata and documentation only; runtime
features are unchanged from 0.1.0a2. Existing local/CI evidence below still applies,
and full tests, distributions, installed examples and README checks are rerun for
the exact release commit before manual Trusted Publisher publication.

**Native iteration rows and datasets remain unsupported.** Generic is the
confirmed target Test type, superseding earlier Automatic-label uncertainty.
API behaviors on Xray 8.5.3-j10 have not been independently verified. User-reported success does not establish those capabilities. Cloud has
synthetic coverage only; Windows/macOS and untested plugin combinations are not
certified. Explicit legacy skip/xfail mappings and incomplete-process limitations
remain documented in the README.

Version 0.1.0 and the Production/Stable classifier describe that bounded feature
scope. Publishing retains the existing manual workflow, reviewed-SHA and artifact
hash checks, `pypi` environment and permissions. No new credentials or workplace
access are involved. The sections below are the **historical prerelease readiness
record**, superseded for release authorization by this scoped decision; they are
retained to distinguish prior concerns from evidence actually obtained.

---

# Release readiness — 2026-10-15

Decision: **not ready for stable publication**. This change prepares reviewable
hardening and complete PyPI usage documentation. Version is prepared as **0.1.0a2**, with the Alpha classifier retained.
Locally rebuilt wheels are validation artifacts, not a published release.
The released 0.1.0a1 on PyPI remains unchanged.

## Executed evidence

All work used `/workspace/pytest-jira-xray-plus`, a separate clone. The preloaded
Ego City repository was not modified. Tests used synthetic data, mocked requests
and the existing localhost fake Xray service. No workplace server or private data
was accessed and no credential was created.

Local environment: Linux, Python 3.12.14, pytest 9.1.1, requests 2.34.2,
pytest-xdist 3.8.0, pytest-rerunfailures 16.7.

- Full suite: **115 passed** (69 original tests plus 46 regression cases).
- New regression coverage: HTTP timeouts and transport failures, bad authentication,
  malformed successful responses, invalid JSON, atomic file preservation,
  setup/call/teardown retries with 0 and 2 workers, collection errors,
  interruption, no-tests sessions, worker crash with and without restart,
  withheld partial uploads, publish-failure exit status in the local report,
  grouped skip/failure semantics, repeated keys within one marker, UTF-8 comment
  bounds and full archival, fail-fast and continue-on-collection-error upload suppression.
- `tools/reproduce.py src --details`: confirms retained passing-case identities
  and failure-before-pass summary. Its nested synthetic pytest failure is expected;
  the verification script itself exits 0.
- `tools/validate_offline.py`: forward and reverse order both retain two local
  cases and both comment identities with aggregate FAIL; transport blocked.
- `tools/check_installed_usage.py`: extracted the actual README example, ran it
  outside the checkout using clean installed-package environments, and checked
  passing/failing local reports plus optional Xray JSON comments. Passed against
  the published PyPI 0.1.0a1 and the proposed wheel. HTTP forbidden during examples;
  pytest loads the installed plugin entry point automatically.
- Built wheel and sdist; `twine check` passed for both. Wheel metadata contains the
  complete README as `text/markdown`. PyPI's `readme_renderer` produced HTML with
  code examples, option tables and troubleshooting sections; preview generated
  as `README-preview.html`. CI uploads this preview for review.
- Ruff passed on changed implementation/new test/tool files; `git diff --check`
  passed. No broad reformat of unrelated inherited files.

CI now runs the suite, probes, distribution checks and installed-wheel README
checks on Python 3.12/3.13/3.14. Its results are separate evidence from the local
Python 3.12 run; consult the PR checks for the latest outcome. No Windows or macOS
execution evidence is claimed.

## Behavior changes for review

- Every HTTP request has connect/read-inactivity timeouts (10/60 seconds) and
  rejects redirects. No automatic retries of imports. A timeout is not proof that
  the server failed to accept an import.
- Authentication must return HTTP 200 with a JSON string token. Import responses
  must be JSON objects with a nonempty execution key. Errors become XrayError;
  no raw response dump or server error body is emitted by the plugin.
- Publishing failures change an otherwise successful pytest exit to 3; an existing
  nonzero result is preserved. Local case JSON captures the final session status.
- Remote uploads are withheld after collection interruption, worker crashes or
  empty marked results; local files may still contain partial observations.
- Rerun reports count as FAIL in legacy Xray aggregation, consistent with the
  conservative local retry summary. Successful retry can still give pytest exit 0.
- Legacy ABORTED-over-FAIL priority and xfail/XPASS mappings remain inherited and
  explicitly documented. Do not infer local and remote summary equivalence.
- Xray JSON file writes are atomic, reject NaN and normalize the output path;
  failed writes preserve existing output. Parameter comments use the safe scalar
  serializer. Repeated keys within one marker do not duplicate evidence/comments.

## Official API review and remaining blockers

The current public [Server/DC JSON format](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301406948)
documents iteration parameters for Manual tests. Its prose and closed schema
still disagree about iteration name. The
[import REST documentation](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301667997)
explicitly says reimports replace dataset and iteration information. These pages
do not establish a version-pinned contract for 8.5.3-j10.

Before a stable release:

1. Obtain successful CI evidence for the declared tested matrix and review the
   changed exit/retry behavior. Decide the exact supported OS/version range.
2. In an independently authorized disposable sandbox, validate the existing
   comment fallback against Xray **8.5.3-j10**, including authentication,
   custom statuses, Unicode, realistic comment size, persisted comments and
   repeated imports on an existing Generic Test, the confirmed target.
   No such live validation was performed in this task.
3. Validate the implemented client comment policy on the target sandbox: default
   32,000 UTF-8 bytes, configurable minimum 256. Oversized comments are shortened
   only after a successful full original payload archive (`--xray-full-report`);
   without an archive export fails. Console and comment both identify truncation.
   The bound is not a universal server limit or a bound on total payload/evidence.
   Structured local case reporting remains unbounded. Local policy tests pass;
   server acceptance still needs validation.
4. If native parameter rows are part of the stable scope, resolve schema and test
   type support with version-specific vendor evidence, then implement behind an
   explicit experimental option and validate stable identity, order, repeat imports,
   readback and per-iteration evidence. **No native implementation is present.**
   The existing static probe files are not proof of support.
5. Subtests, repeat-plugin semantics, reliable identity across crashed/restarted
   workers and cross-session aggregation need separate design if required.
   Hard termination cannot guarantee final report writing.
6. Finish independent PR review before merge or publication. Version, release notes
   and the manual `publish.yml` exact artifact checks are prepared for **0.1.0a2**.
   The `pypi` environment, workflow_dispatch-only trigger, explicit publish opt-in,
   reviewed-SHA check and permissions remain unchanged. No dispatch occurred.
   Do not republish this changed build as 0.1.0a1 or label it stable.

The full README is packaged for the next approved release. A PR alone does not
update the published PyPI long description. Publishing a new version remains a
separate decision after these gates; this task performed no publication.

## Proposed prerelease artifacts

- `pytest_jira_xray_plus-0.1.0a2-py3-none-any.whl`
- `pytest_jira_xray_plus-0.1.0a2.tar.gz`

CI uploads both in `prerelease-distributions-python-3.12` (and equivalent 3.13/3.14
artifacts); each build prints SHA-256 hashes. The separate README preview artifact
allows inspection of the full packaged description. The next PyPI upload is not
performed until independent review is complete.

The [minimal sandbox check](MINIMAL-SANDBOX-CHECK.md) separates implemented comment
validation from a three-import anonymous-native-row capability probe. Neither
requests private credentials or data. Current official docs do not supply a
version-pinned Generic/name contract; this remains an explicit blocker.

## Release authorization update

Independent review approved the implementation at df9ddd86 for experimental alpha.
The release guide now targets 0.1.0a2. Merge and manual publication are authorized
after green checks; the stable-release limitations above remain in force. Earlier
“proposed” and review-pending notes record the preparation stage, not a stable claim.


## 0.1.2 integration-first documentation release

Jira with Xray is the required product foundation. The README, website and package
summary now lead with prerequisites, existing Test/Test Execution mapping, Server/DC
authentication, preview and import. Offline exports and case JSON remain available
as integration preview/debugging/audit facilities; no runtime files change.

Generic is the confirmed target Test type. Independent live validation of Xray
8.5.3-j10 authentication/permissions and resulting aggregate Test Runs remains
outstanding.
Native iteration rows, datasets and per-iteration evidence are not implemented.
Synthetic import tests and offline commands do not establish server compatibility.

A GitHub read request briefly returned HTTP 401 (Bad credentials). After reporting
the denial, the same read-only request succeeded with existing authorization; no
credentials or permissions were changed. PyPI publication remains a separate step
through the existing manual workflow after review and CI.

Local 0.1.2 validation: 115 tests passed; all 14 reordered README commands passed
against a clean installed wheel with HTTP blocked; full wheel metadata Markdown
rendered and both distributions passed Twine checks. All 13 runtime module files
match the installed public 0.1.1 package byte-for-byte. The strict site build,
internal links and desktop/mobile browser checks passed. This evidence does not
replace the outstanding server validation or authenticate a live import.

The 0.1.2 release uses the existing manual `publish.yml` workflow and `pypi`
environment. Exact artifact/version checks advance from 0.1.1 to 0.1.2; permissions,
Trusted Publisher identity and runtime source are unchanged. The workflow verifies
the reviewed commit, tests, installed examples and artifact hashes before publishing.
Publication success must be verified from the workflow result and public PyPI files.


## 0.1.3 Generic target documentation release

Michael confirmed Generic as the target Test type and approved merging the correction,
updating Pages and publishing stable 0.1.3. This supersedes the earlier uncertainty
about an Automatic display label. The implementation still imports aggregate results
for existing Jira Test keys and does not provision, infer or change their type.
Jira with Xray remains required for the intended integration; native iteration rows,
datasets and per-iteration evidence remain unsupported. Independent live import
validation on Xray 8.5.3-j10 remains outstanding.

Runtime source is unchanged from 0.1.2. The existing manual Trusted Publisher workflow
retains its permissions and pypi environment; only exact version/filename checks advance
to 0.1.3. Publication must be verified against the reviewed remote commit, CI artifact
hashes, public package metadata and a fresh public-PyPI installation.


## 0.1.4 attachment ownership candidate — 2026-10-16

Unpublished candidate; 0.1.3 remains the published baseline. PyPI's public JSON
reported 0.1.4 unused when preparing this iteration; recheck immediately before
publication. The only runtime change copies the incoming evidence/defect list
containers in TestCase. Evidence dictionaries are not deep-copied; aggregation
appends entries and does not mutate their fields. Identical attachment occurrences
remain distinct. Defects still de-duplicate and statuses/comments are unchanged.

Synthetic tests cover a shared-key case followed by a single-key case, and two
parameter cases sharing both keys, in both orders and serial/xdist execution.
Requests transport is blocked and results are written locally. Native iterations,
custom Test-type mapping and live Xray 8.5.3-j10 behavior remain unverified.

The candidate updates only version literals/artifact filenames in publish.yml;
reviewed-SHA checks, artifact hashes, pypi environment, permissions and opt-in
remain intact. No publication, deployment or merge is part of candidate preparation.
Independent review and exact-head CI are required before the standing maintainer
authorization may be exercised. Current evidence and state are in the task ledger.


## 0.1.5 defects-validation candidate — 2026-10-16

Baseline release: 0.1.4. Candidate 0.1.5 was unused at preparation; recheck before
publication. Malformed defects now generate a standard collection-failure report
and clear runnable items before fixtures. This reaches the xdist controller and
withholds uploads, even if collection errors are configured to continue. Raising
UsageError in this hook alone caused an xdist worker-finish assertion during
regression development, so the candidate uses pytest's collection-report hook.

Only list shape and nonempty string elements are checked; valid empty lists,
original values and aggregation remain unchanged. No Jira-key regex, server access
or marker-value formatting is added. Serial/xdist, preview/upload, disabled-mode
and collect-only compatibility regressions use synthetic data and forbidden transport.
Collect-only still disables Xray reporting and does not validate defects markers.

Publisher changes are version literals only. Candidate preparation does not
merge or publish. Independent review, current receipts and exact-head CI remain
required. Browser certificate/security errors must block browser verification
and require user handoff; never bypass them. Normal HTTPS checks are separate.


## 0.1.6 shared-status README candidate — 2026-10-16

0.1.5 is published and verified. PR #13 enabled the independently reviewed,
explicitly approved GitHub Release job. Backfill 38909839526 created v0.1.5 at
its original published commit; both public GitHub assets matched PyPI hashes.
Retry 38909920867 preserved release and asset identities, hashes and timestamps.

Candidate 0.1.6 delivers the shared README's six relevant status badges to PyPI.
Runtime, dependencies and accepted tag/coverage tooling are unchanged. Publisher
changes are version literals only; SHA/artifact checks, opt-in, pypi environment
and permissions remain unchanged. The currently published coverage snapshot is
95.8% plugin lines / 87.9% branches at clean 0.1.5, with explicit provenance;
new snapshots must be measured and verified, never inferred from a prior version.

0.1.6 was unused at preparation; recheck immediately before publication. Required
profiles, installed commands, badge rendering/URLs, exact-head CI and fresh
independent review precede publication. Then verify public PyPI bytes and README,
automatic GitHub tag/Release/assets and Pages. Never bypass a browser security
warning; the existing certificate failure remains a user handoff. Native iterations
remain unsupported; custom Automatic mapping and live Xray 8.5.3-j10 remain unverified.


## 0.1.7 collection-validation candidate — 2026-10-17

The candidate bundles independently accepted PR15–17: set membership in collection
validation, controlled malformed Test-key failures, and controlled duplicate-policy
failures. Diagnostic order, repeated-key deduplication, opt-in grouping and privacy
settings remain unchanged. Duplicate-policy exits intentionally use collection-error
classification rather than INTERNALERROR/exit 3; the full README explains recovery.

PR17 merged at bd231e13702fec4153499aa59a9f815f5d74f475 with identical accepted tree
and all main CI green. This release preparation freezes that runtime. Package and
trusted publisher changes are version literals only; no dependency/permission changes.
0.1.7 was unused at preparation; recheck immediately before eventual publication.

All five profiles, installed tutorial/full metadata rendering, badge endpoint checks,
exact-head CI and fresh independent review gate publication. After acceptance,
verify publisher/public PyPI/GitHub byte hashes, fresh public install and examples,
automatic tag/release target, and refreshed Pages/status/coverage with actual source
provenance. Current public snapshots describe 0.1.6, not a measurement of 0.1.7.
Browser certificate warnings must not be bypassed; prior PyPI HTML client challenge
and live visual gaps require truthful reporting. Generic Xray 8.5.3-j10/custom
Automatic mapping remains unverified live; native iterations/datasets unsupported.


## 0.1.7 published; cleanup-failure candidate — 2026-10-17

0.1.7 publication and public installation are verified in
[release evidence](agent/evidence/XRAY-RELEASE-003-release-0.1.7.json): reviewed
source98b56da, matching PyPI/publisher/GitHub files, all 14 installed commands and
101 live Pages files. Clean source coverage measured 96.2% lines and 89.2% branches;
public metadata explicitly identifies local measurement. These supersede the
preparation-time 0.1.6 snapshots above.

The next unreleased candidate changes only the two report writers' temporary
cleanup handling. Synthetic permission failures reproduced raw cleanup exceptions
masking primary failures in 0.1.7. No version bump, workflow or dependency changes.
All five profiles and exact-head CI plus independent review gate merge; release
requires a separate reviewed version candidate. No live server proof is implied.
Existing browser certificate handoff and PyPI HTML client challenge remain.


## Authentication configuration candidate — 2026-10-17

PR19 cleanup handling merged at 3f144256ca910e37a64fb0542c16d6d7faa685f7 after
independent acceptance and six green acceptance-head workflows; all three main
workflows passed. It remains unreleased alongside this next bounded improvement.

Missing authentication settings currently raise internal configuration errors.
The candidate changes plugin.py to translate expected helper XrayError into pytest
UsageError with its existing diagnostic. No helper, HTTP, TLS, auth-selection,
version, dependency, workflow or permission changes. Synthetic baseline matrix:
22 expected failures and three passing credential-free modes before the fix.
All five profiles, installed tutorial and exact-head CI plus independent review
gate merge. A later milestone needs separately reviewed release preparation.
Published 0.1.7 and its verified public evidence remain the release baseline.
No live Xray or browser validation is implied.


## Report path configuration candidate — 2026-10-17

PR20 merged at 0d3c5f0086771eccb898f8b509839c4f725778a3 after independent acceptance,
six acceptance-head workflows and three main workflows passed. Its authentication
fix and PR19 cleanup handling remain unreleased for a meaningful later milestone.

This candidate converts OSError/RuntimeError raised during initial report-path
normalization into option-specific usage errors. It preserves non-strict resolve,
valid expansion/collision behavior and writer semantics. Python3.12 raises on
symlink loops during normalization; Python3.13+ can defer that failure to writing.
This is not filesystem preflight or protection against filesystem races. Initial
synthetic matrix reproduced 21 failures and seven passes; additional collect-only
and unexpected-exception preservation cases passed before edits.

All five profiles, installed guide, exact-head CI and independent review gate
merge. No version/dependency/workflow/permission changes or live-server claims.
Published0.1.7 and existing browser-security/PyPI HTML limits remain the baseline.


## 0.1.8 error-handling release candidate — 2026-10-17

The candidate groups independently accepted PR19–21: preserve report-writing
errors when cleanup also fails, classify existing authentication setup errors as
usage errors, and classify raised path normalization errors with the responsible
option. The full guide explains exit4 versus prior exit3, retained report data,
cleanup residuals and the Python3.12/3.13+ symlink-loop boundary.

Reviewed merge provenance:
- PR19: `3f144256ca910e37a64fb0542c16d6d7faa685f7`
- PR20: `0d3c5f0086771eccb898f8b509839c4f725778a3`
- PR21/release baseline: `a9279d81e674ceb5bdfa8f72d3cf713a96d49f84`

All main workflows passed on that exact baseline. Runtime/tooling/dependencies
are frozen. Package and trusted-publisher changes are version literals only;
permissions, explicit opt-in, pypi environment, reviewed SHA and artifact checks
remain unchanged. Public PyPI latest0.1.7 and unused0.1.8 verified at preparation;
recheck immediately before eventual publication.

All five profiles, installed tutorial/full README rendering, shared badge checks,
exact-head CI and fresh independent release review gate merge/publication. Public
coverage/status still describe verified0.1.7; no new0.1.8 measurement is claimed.
After acceptance, verify publisher/PyPI/GitHub artifact hashes and tag, fresh public
installation/all14 commands, deployed Pages/status and actual coverage provenance.
Do not bypass browser certificate warnings. PyPI HTML Client Challenge and live
visual gaps remain; previews/HTTP checks are not live visual proof. Generic on-prem
8.5.3-j10/custom Automatic mapping remains unverified live; native iterations and
datasets are unsupported.


## Unreleased blank base-URL guard — 2026-10-17

Published 0.1.8 is verified at source 074c09a79e5578d89138c4207556b99005e08608.
Publisher 39007135770, automatic GitHub release 39007292690 and Pages deployment
39007332906 passed. Both public assets match publisher hashes and the source tag;
fresh public-index installation passed all 14 README commands. All 101 live Pages
files match deployment bytes. Fresh clean-source local coverage is 753/770 lines
(97.8%) and 222/244 branches (91.0%), with 383 tests + 19 subtests. Proof is in
`docs/agent/evidence/XRAY-RELEASE-004-release-0.1.8.json`.

This candidate changes only the base-option helper's blank-value guard. A
transport-blocked installed 0.1.8 reproduction shows tests run before MissingSchema
for both empty/whitespace URLs in basic, API-key and Cloud modes. The candidate
rejects blank values through the existing configuration UsageError boundary,
without general URL validation, trimming or credential/TLS/runtime HTTP changes.
The version remains 0.1.8 until a separately reviewed release decision. Full
profiles, installed documentation and exact-head CI plus fresh independent review
are required before merge. No new live Jira/Xray compatibility claims follow.
The certificate-warning handoff and PyPI HTML Client Challenge remain; local
previews and normal-TLS metadata checks are not live rendered-page proof.


## Unreleased result aggregation scaling — 2026-10-17

PR23 was independently accepted and merged at 2b8a4f29567bc612a758635975da09e1c1439f15.
All six acceptance-head workflows and main 39008642922/39008642908/39008642928
passed. It remains grouped for a later release; latest published baseline is 0.1.8.

The next candidate changes only xray_plugin.py's report-stream lookup: a private
per-instance index references the same TestCase objects already appended to the
execution list. Public helper/model code and final-payload customization remain
unchanged. This costs one dictionary entry per unique key and assumes ownership
of the live plugin accumulator, not concurrent external mutation of its internals.
No overall linear-time or bounded comment-memory claim is made.

Six operation-count regressions fail on the old linear lookup. The same synthetic
2k/4k/8k report stream measured roughly 0.043/0.160/0.605 seconds on installed 0.1.8
and 0.004/0.008/0.015 seconds on the candidate in this environment. These are
illustrative single local measurements, not portable performance guarantees;
regressions use comparison counts rather than elapsed-time thresholds. Full
profiles, installed guide and CI plus fresh independent review are required.
No version, publishing, permission or live Xray capability changes are included.


## Unreleased local-report parent directories — 2026-10-17

PR24 independently accepted and merged at 285cd6dfa9cc8303587bef930d0902597d361e17
with identical accepted tree. Six acceptance-head workflows and main CI
39009983118/39009982918/39009982930 passed. No publication; baseline remains 0.1.8.

Installed 0.1.8 reproduces a passing test followed by exit 3 and no nested case
report in serial/xdist when parents are absent. Eight new path/outcome regressions
fail on that baseline. The candidate adds controller-side parent creation after
JSON serialization, before the owned temporary file; no permission bypass or
directory rollback. Blocking files and denied creation remain write failures.
An existing write-failure test now uses a blocking parent file, retaining its
warning/exit assertions and checking that the blocking file survives.

The full guide and schema notes distinguish the candidate from 0.1.8. The installed
usage checker retains all fourteen commands and adds a fifteenth nested-report
command with absent parents before execution and schema/case/phase assertions.
All five profiles, exact-head CI and fresh independent review are required before
merge. No version, dependency, workflow, permission or live Xray changes. Group
this with other accepted work for a later release. Existing live-browser and
Generic/custom Automatic validation limits remain; native iterations unsupported.
