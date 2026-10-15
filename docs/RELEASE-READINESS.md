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
