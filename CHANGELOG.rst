Unreleased
==========
- Update pinned setup-python action to 7.0.0 while retaining the Python matrix.
- Update pinned checkout action to 7.0.1 with fresh dependency-maintenance evidence;
  preserve credential opt-outs and workflow security checks. No package release.

0.1.10 [2026-10-23]
===================
- Reject explicitly empty report filenames with usage-error exit 4 before tests
  or upload selection. Previously --xraypath= could select upload and empty case
  or full-report paths could silently disable requested output. Keep omitted
  options, collect-only, nonempty paths and valid reporting unchanged.
- Configure Friday Dependabot checks for Python manifests and GitHub Actions,
  grouping minor/patch updates while keeping majors separate for review.
  No dependency upgrades, automatic merges or package release in this setup.
- Correct repository documentation link checks for named pages such as
  class_index.html: only an exact index.html filename represents a directory.
  Preserve genuine missing-file/fragment errors; plugin behavior is unchanged.


0.1.9 [2026-10-17]
==================
- Omit xdist worker-header-only comments when a report has no diagnostic
  representation, preventing otherwise passing grouped exports from exhausting
  comment limits. Preserve actual/custom diagnostics, privacy opt-ins and limits.
- Preserve opt-in reports when integer parameters exceed Python's decimal
  conversion limit at capture time: use the existing unsupported-value
  placeholder instead of losing the case report or aborting parameter comments.
  Keep valid integers, privacy defaults and interpreter settings unchanged.
- Create missing parent folders for requested local case reports at write time,
  matching preview/archive exports. Preserve genuine filesystem errors, atomic
  replacement and prior files; newly created folders can remain after failure.
- Avoid repeated linear Test-key scans during plugin result aggregation. Preserve
  first-observed ordering, grouping contents/statuses, public model APIs and final
  payload hooks, at the cost of one index entry per unique Test key.
- Reject empty or whitespace-only upload base URLs as configuration usage errors
  (exit 4) before tests run, instead of failing later while preparing an upload
  (exit 3). Preserve nonblank values and credential-free offline/collect-only modes.

0.1.8 [2026-10-17]
==================
- Report expected path expansion/resolution failures as option-specific pytest
  usage errors (exit 4). Preserve non-strict resolution, expansion conventions,
  collision checks and write-time failures, including Python's symlink-loop
  behavior difference between 3.12 and 3.13+.
- Report missing authentication environment variables and nonexistent CA bundle
  paths as concise pytest usage errors (exit 4), avoiding configuration internal
  tracebacks/exit 3. Offline/collect-only and runtime HTTP handling are unchanged.
- Preserve report-writing errors when temporary-file cleanup also fails, keeping
  the existing Xray error or offline warning/exit handling and identifying the
  leftover temporary path. Skip cleanup after successful atomic replacement.

0.1.7 [2026-10-17]
==================
- Classify disallowed duplicate Test keys as collection failures, avoiding internal
  errors and xdist worker/controller errors while preserving diagnostic order and
  opt-in grouping. Nonzero collection-error exits replace internal-error exit 3.
- Report malformed Test-key markers as collection errors before fixtures or
  uploads, including xdist and continue-on-collection-errors, instead of
  internal errors. Preserve valid marker forms and duplicate-key policy.
- Use set membership for duplicate Test-key collection validation, avoiding
  quadratic list scans for large suites while retaining diagnostic order,
  repeated-key handling and opt-in grouping. No new flags or default changes.

0.1.6 [2026-10-16]
==================
- Recheck a draft's tag before publication and verify the returned published
  release identity/state and tag target; never report success for a retargeted draft.
- Add relevant shared README badges and first-party measured coverage/metadata
  snapshots, with explicit scope, provenance and freshness. No external account.
- Measure all plugin source files including Python subprocesses in the existing
  read-only Python 3.12 CI job; retain the full 3.13/3.14 matrix.
- Enable automatic version tags and GitHub Releases after verified PyPI publication,
  with exact artifacts, version notes, safe retries and conflict protection.
- Add beginner release/backfill instructions after explicit permission confirmation
  and independent review; verify the 0.1.5 tag, artifacts and idempotent retry.
- Publish shared README badges in PyPI metadata. No plugin runtime changes.

0.1.5 [2026-10-16]
==================
- Validate malformed defects markers during collection when Xray reporting is on,
  before fixtures or uploads, including xdist and continue-on-collection-errors.
- Report a fixed collection error without displaying marker values or invoking
  arbitrary repr. Valid lists, including empty lists, retain their string values;
  no Jira-key format regex is imposed. Reporting-disabled runs remain unaffected.
- Document beginner configuration fixes and retain the prohibition on bypassing
  browser certificate/security warnings.

0.1.4 [2026-10-16]
==================
- Isolate evidence and defect list ownership per mapped Jira Test key. A later case
  for one key no longer changes another key's attachments or defects.
- Prevent attachment inflation when parameter cases map to the same multiple keys;
  retain legitimate identical attachment occurrences, status precedence and comments.
- Add serial/xdist offline regressions for mixed/shared mappings in both orders.
- Document repository-specific standing maintenance authorization without weakening
  independent review, evidence, CI or trusted-publishing safeguards.

0.9.4 [2026-04-24]
==================
- Fixed missing test evidences for tests with same Jira XRAY ID

0.9.3 [2025-10-11]
==================
- Fixed XRAY report for uploading to existing test execution

0.9.2 [2025-05-24]
==================
- Fixed handling 504 http error from server
- Removed support for Python 3.7 and 3.8

0.9.1 [2024-10-27]
==================
- Improved error handling in Jira response

0.9.0 [2024-07-19]
==================
- Added support for marking tests with defects

0.8.11 [2024-03-27]
===================
- Improved errors handling

0.8.10 [2023-09-08]
===================
- Added default text for mandatory `summary` field if not provided by a user

0.8.9 [2023-07-11]
==================
- Fixed formatting issues with pytest captures

0.8.8 [2023-06-06]
==================
- Added option to capture pytest stdout and logs in Xray report

0.8.7 [2023-05-29]
==================
- Fixed sending multiple results while running with xdist

0.8.6 [2023-05-15]
==================
- Changed key ``ContentType`` to ``contentType`` in Xray report

0.8.5 [2023-03-13]
==================
- Added possibility to disable certificate verification in client secret authentication

0.8.4 [2023-02-09]
==================
- Fixed wrong finished date in the Xrey report

0.8.3 [2023-01-02]
==================
- Fixed using plugin with xdist
- Removed redundant Token authentication

0.8.2 [2022-08-25]
==================
- Added possibility to attach test evidence

0.8.1 [2022-08-05]
==================
- Added hook to modify XRAY results before publishing

0.8.0 [2022-05-23]
==================
- Added token authentication
- Changed CLI options
  - Basic authentication is default for both Jira DC and cloud
  - Changed option `--api-key` to `--api-key-auth`

0.7.1 [2022-05-11]
==================
- Improved printing error messages from a Jira server

0.7.0 [2022-03-09]
==================
- Allow optional duplication of ids
- Minor fixes to support the latest changes in Xray Cloud

0.6.0 [2022-02-26]
==================
- Added API Key Authentication
- Added possibility to use multiple jira ids in the marker

0.5.1 [2022-02-17]
==================
- Fixed endpoint for Jira Cloud

0.5.0 [2021-12-10]
==================
- Added support for test execution revision
- Added support for summary and description
- Added support for executions test environments and fix version

0.4.0 [2021-11-28]
==================
- Fixed missing statuses in XRAY report (errors, xfail, xpass)

0.3.0 [2021-10-13]
==================
- Added option to save test execution results to JSON file

0.2.1 [2021-10-11]
==================
- Bug fixes

0.2.0 [2021-09-22]
==================
- Added support for Xray Cloud

0.1.2 [2021-04-24]
==================
- Added SSL Verification

0.1.1 [2021-04-11]
==================
- Fixed handling http errors

0.1.0 [2021-02-12]
==================
- First release

0.1.0a2 (2026-10-15)
-------------------

* Bound HTTP connect/read waits; validate authentication and import responses.
* Surface publishing failure with a nonzero exit; withhold incomplete remote imports.
* Preserve failed retry phases in legacy aggregation and write local exports atomically.
* Add failure, retry and worker regression coverage, installed-wheel CI checks,
  and complete beginner usage documentation for the PyPI long description.
* Keep native iterations unimplemented and stable publication blocked on target validation.

* Add configurable UTF-8 comment bounds with required full local archival before
  truncation, and prevent partial uploads after fail-fast or collection failures.
* Prepare exact 0.1.0a2 artifacts in the existing manual publishing workflow;
  publication uses the existing manual approval workflow.

0.1.0 (2026-10-15)
------------------

* Release the validated 0.1.0a2 feature set as stable: local case/attempt reporting
  and optional aggregate Xray comments, including bounded comments with full
  local archival, transport failure handling and partial-upload suppression.
* Michael reported successful validation and explicitly authorized stable
  publication. This is user-reported evidence, not independent observation of
  exhaustive server behavior or confirmation of Automatic's effective Test type.
* No runtime feature changes from 0.1.0a2. Native iteration rows and datasets
  remain unsupported; documented platform/plugin and status-mapping limits apply.

0.1.1 (2026-10-15)
------------------

* Replace the option-heavy introduction with a progressive, runnable tutorial
  covering local reports, values/identity choices, failures, offline Xray export,
  full comment archival and optional upload. Keep reference material below it.
* Execute tutorial commands and check actual report excerpts against installed
  wheels in CI. Replace obsolete README.rst guidance with a maintained-guide link.
* No runtime feature changes or expanded compatibility claims.


0.1.2 (2026-10-15)
------------------
- Correct Jira/Xray integration positioning: Jira with Xray is the required product foundation.
- Lead the complete guide with prerequisites, Test/Execution mapping, authentication and import.
- Retain offline preview, local case audit and archives as integration support facilities.
- No runtime changes, network enforcement, credentials or publishing permission changes.


0.1.3 (2026-10-15)
------------------
- Confirm Generic as the target Test type on Jira Server/Data Center with Xray 8.5.3-j10.
- Correct README, website and compatibility guidance; retain native-iteration limitations.
- Documentation-only release: runtime, credentials and publishing permissions unchanged.
