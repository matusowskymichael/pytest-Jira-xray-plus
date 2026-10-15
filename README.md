# pytest-Jira-xray-plus

**[Start here: runnable quick start](https://github.com/matusowskymichael/pytest-Jira-xray-plus#quick-start-no-jira-required)**

Keep every parametrized pytest case in a local JSON file, and optionally put
case details into one Jira/Xray Test Run comment. A **case** is one set of inputs;
a **Test Run** is Xray's result for one Jira Test issue in a Test Execution.
This package does **not** create native Xray iteration rows or datasets.

[0.1.0a1 is published on PyPI](https://pypi.org/project/pytest-jira-xray-plus/0.1.0a1/).
It is an experimental alpha, not a stable release. Version **0.1.0a2 is prepared but not published** while PR review is outstanding.
This guide includes its proposed hardening changes, clearly identified below. The installation and local examples
work with the published alpha as well as the proposed changes.

This is an independent Apache-2.0 fork of
[pytest-jira-xray](https://github.com/fundakol/pytest-jira-xray), based on upstream
commit `6ac1117585da590001cdbc2bf261b78683c19dcb` (0.9.4 line).

## Quick start (no Jira required)

Use Python **3.12 or newer**. The tested local baseline is Python 3.12.14,
pytest 9.1.1, requests 2.34.2, pytest-xdist 3.8.0 and pytest-rerunfailures 16.7
on Linux. Metadata permits pytest `>=9.1.1,<10` and requests `>=2.34.2,<3`;
that is not a promise that every future version or OS has been tested.
CI checks Python 3.12, 3.13 and 3.14; see its results before relying on those environments.

Create an empty folder and a fresh Python environment. The environment isolates
this installation from other projects. These commands use a POSIX shell:

```sh
mkdir xray-demo
cd xray-demo
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install pytest-jira-xray-plus==0.1.0a1
```

On Windows, use `py -3.12 -m venv .venv` and activate with
`.venv\Scripts\Activate.ps1` in PowerShell or `.venv\Scripts\activate.bat`
in Command Prompt. Subsequent `python -m ...` commands are the same.
No Git checkout, Jira account, credentials, or configuration file is required.
Installation downloads packages; the following test runs do not contact Jira.

**Do not install `pytest-jira-xray` in this environment.** Both distributions
provide the same Python module (`pytest_xray`) and pytest plugin name (`xray`).
They overwrite each other's files. If both were installed, start with a new
environment; disabling one plugin does not repair overwritten files.

Create a file named **`test_example.py`** in `xray-demo`, next to `.venv`:

```python
import pytest

@pytest.mark.xray("DEMO-1")
@pytest.mark.parametrize(
    "value, expected",
    [(1, 2), (2, 3)],
    ids=["one-plus-one", "two-plus-one"],
)
def test_add_one(value, expected):
    assert value + 1 == expected
```

`parametrize` runs the function twice. The readable `ids` identify each input
set. `DEMO-1` is a placeholder Jira Test key; it is not looked up locally.
The marker is only needed for the optional Xray export later.

```sh
python -m pytest -q test_example.py --xray-case-report=cases.json
```

Expected: **2 passed**, exit code 0, and **`cases.json`** in the current folder.
It has two separate `cases`, each with its node ID (test path plus input ID),
`status: "passed"`, and an `attempts` list recording setup, call and teardown.
Setup prepares fixtures, call runs the test, and teardown cleans up. Parameter
values and failure text are excluded from this file by default. Inspect it with:

```sh
python -m json.tool cases.json
```

To see a failure, change `(2, 3)` to `(2, 99)` and rerun. Expect **1 failed,
1 passed**, exit code 1, and two preserved case records, one failed and one
passed. The file is replaced on each run: use different paths to keep history.
**`cases.json` is not Xray import JSON.** Do not upload it to Xray.

## Optional: preserve parameter details in an Xray comment

With the same example, run:

```sh
python -m pytest -q test_example.py --xray-case-report=cases.json \
  --jira-xray --xraypath=xray.json --allow-duplicate-ids \
  --xray-parameter-details
```

This writes **`xray.json`** beside **`cases.json`**. No upload occurs because
`--xraypath` selects a file. Keep that option for all offline Xray experiments,
including when `--jira-xray` comes from `pytest.ini` or `PYTEST_ADDOPTS`.

`xray.json` has one entry for `DEMO-1`: both cases share the same Jira key.
Its comment contains both case identities, scalar input values, phase and
outcome. With the original example its status is `PASS`; with the intentional
failure it is `FAIL`. `--allow-duplicate-ids` permits this grouping; without
it repeated Jira keys are rejected. Multiple keys can be given as
`@pytest.mark.xray("DEMO-1", "DEMO-2")`, which copies the result to both Tests.

The fallback is opt-in because comments can expose data and grow large.
Published 0.1.0a1 has no size limit. Proposed 0.1.0a2 uses a **32,000 UTF-8 byte
limit per final comment**, configurable with `--xray-comment-limit` (minimum 256).
This is our conservative client policy, not a universal Jira/Xray server limit;
a server may impose a different limit. The bound includes the truncation notice
and any wiki formatting wrapper, but does not bound evidence or total request size.

In 0.1.0a2, add `--xray-full-report=full-xray.json` to preserve the **entire
original Xray payload** locally before shortening any comments. The main export
(either `xray.json` or the upload) then contains a clearly marked shortened
comment, and pytest prints how many comments were truncated. Without a full-report
path, an oversized comment stops export with a nonzero exit rather than silently
losing detail. If writing the archive fails, export also stops. Status and evidence
are never truncated. Keep `cases.json` for structured cases/attempts; it remains
unbounded and is independent of the full-payload archive.

`full-xray.json` contains full comments, values, failure text and evidence: protect
it like the original test data. It is replaced each run; use a unique path to keep
history. It must differ from `cases.json` and `xray.json`. Do not upload it to
bypass the chosen bound. This extra file is written only when explicitly requested.
Check `xray.json` before use and keep both local reports when exporting large suites.
A successful import should show one aggregate Test Run and its comment, **not
separate native iteration rows**. Actual rendering on Xray 8.5.3-j10 is unverified.
Only parametrized reports get the extra parameter comment. Failure text is
included in legacy comments even without this option.

Use synthetic inputs and safe explicit IDs. IDs can contain data even when
values are excluded. `--xray-case-redact-identities` replaces names and IDs
**only in `cases.json`**; it does not redact console output, `xray.json`,
comments, captures or evidence. Non-scalar and non-finite values get a placeholder
in the proposed hardening; alpha 0.1.0a1 only filters non-scalar objects in comments.
Indirect fixtures record their input parameters, not the fixture's return value.

## Optional: send results to Jira/Xray Server or Data Center

Only do this in an authorized disposable test project first. No workplace server
was accessed to develop or verify this package. The target **Xray 8.5.3-j10** and
the custom **Automatic** type's apparent Generic mapping remain unverified.
Ask the administrator to confirm the actual type; the label alone is insufficient.

Replace `DEMO-1` in your test with an existing sandbox **Test** key. Obtain an
existing sandbox **Test Execution** key, for example `DEMO-100`. The following
Bash example reads an existing personal access token without putting it
in shell history. Use your CI's protected environment variables for automation;
do not commit credentials or put them in pytest options.

```sh
export XRAY_API_BASE_URL='https://jira.example.invalid'
read -r -s -p 'Existing sandbox Jira token: ' XRAY_API_KEY
printf '\n'
export XRAY_API_KEY
python -m pytest -q test_example.py --jira-xray --api-key-auth \
  --execution=DEMO-100 --allow-duplicate-ids --xray-parameter-details \
  --xray-case-report=cases.json
unset XRAY_API_KEY
```

The `.invalid` URL is a nonworking placeholder: replace it with the authorized
sandbox base URL, including Jira's context path if any, but no REST suffix.
This command **uploads**, because `--xraypath` is absent. It submits one JSON
request to `/rest/raven/2.0/import/execution`. Do not use `--cloud` for Server/DC.
On success pytest prints the returned Test Execution ID. Inspect the Test Run's
comment in that execution. Permissions, custom statuses, proxy configuration,
comment limits and API response shape need sandbox validation.

Supplying `--execution` updates that execution. Omitting it asks Xray to create
an execution using the report metadata, subject to server requirements.
Reimporting can replace existing Test Run details, including dataset/iteration
data; use a disposable execution. The official
[Server/DC import API](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301667997)
documents this replacement behavior. This package does not retry imports automatically:
a timeout can occur after a server accepted a request. Check the execution before retrying.

Authentication choices (choose one):

| Choice | CLI option | Environment variables |
| --- | --- | --- |
| Jira personal access token | `--api-key-auth` | `XRAY_API_BASE_URL`, `XRAY_API_KEY` |
| Basic authentication, if enabled by your Jira administrator | none | `XRAY_API_BASE_URL`, `XRAY_API_USER`, `XRAY_API_PASSWORD` |
| Xray Cloud client credentials, advanced and not target-validated | `--cloud --client-secret-auth` | `XRAY_API_BASE_URL`, `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` |

Cloud uses the Xray API base URL, `/api/v2/authenticate` and
`/api/v2/import/execution`; it is a different service from the Jira URL.
`--cloud` changes status strings to `PASSED`/`FAILED`, and does not convert
Generic tests into Manual tests or enable native iterations. Cloud behavior
has only synthetic tests, not live validation.

TLS certificate verification is on by default. `XRAY_API_VERIFY_SSL` accepts
`True`, or a path to a trusted CA certificate bundle for an internal CA.
`False` disables verification and should not be used with real credentials.

Optional execution metadata is read from these environment variables:

| Variable | What it changes |
| --- | --- |
| `XRAY_EXECUTION_SUMMARY` | Execution title; default for a new execution is `Execution of automated tests` |
| `XRAY_EXECUTION_DESC` | Execution description |
| `XRAY_EXECUTION_REVISION` | Revision, for example a commit ID |
| `XRAY_EXECUTION_TEST_ENVIRONMENTS` | Environment names separated by whitespace |
| `XRAY_EXECUTION_FIX_VERSION` | Fix version; the first nonempty parsed value is used |

## All package options

See `python -m pytest --help` for pytest's own options.

| Option | Effect |
| --- | --- |
| `--xray-case-report=PATH` | Write all observed cases locally; no Jira needed. Parent folder must exist. |
| `--xray-case-values` | Include scalar input values in that local report; requires `--xray-case-report`. |
| `--xray-case-redact-identities` | Replace local names/IDs with per-run aliases; requires the report and cannot combine with case values. |
| `--jira-xray` | Enable the legacy marked-test exporter. Uploads unless `--xraypath` is set. |
| `--xraypath=PATH` | With `--jira-xray`, write Xray JSON to a file instead of uploading; creates parent folders. |
| `--allow-duplicate-ids` | Merge cases sharing a Jira Test key; required for the example's parametrization. |
| `--xray-comment-limit=BYTES` | Proposed 0.1.0a2: bound each final comment in UTF-8 bytes; default 32000, minimum 256. |
| `--xray-full-report=PATH` | Proposed 0.1.0a2: save full original legacy payload before comment truncation; requires `--jira-xray`. |
| `--xray-parameter-details` | With `--jira-xray`, add parameter identities and scalar values to comments. |
| `--execution=KEY` | Update an existing Test Execution. |
| `--testplan=KEY` | Set the Test Plan key in execution metadata. |
| `--api-key-auth` | Use `XRAY_API_KEY` as a Bearer token. |
| `--client-secret-auth` | Authenticate with Xray Cloud client credentials. |
| `--cloud` | Use Cloud endpoint and status spelling. |
| `--add-captures` | Include captured stdout, stderr and logs in legacy comments; may expose secrets. |

No options enable native iterations. `--collect-only` does not create reports.
Use different output paths for the two report formats. Local report identity
aliases are assigned in arrival order and cannot be compared across sessions.

## Results, retries and exact limitations

| Event | Local case summary | Legacy Xray summary |
| --- | --- | --- |
| Passing call | passed | PASS |
| Failed call or fixture setup/teardown | failed | FAIL |
| Skip | skipped | ABORTED |
| Expected failure (`xfail`) | skipped, with xfail recorded | FAIL (inherited mapping) |
| Unexpected pass (`xpass`) | passed, with xpass recorded | PASS |
| Strict unexpected pass | failed | FAIL |
| Failed attempt then successful retry | failed, both attempts kept | FAIL in proposed hardening; alpha may incorrectly show PASS |

The local report deliberately remembers any failure, even if pytest's retry
plugin eventually exits 0. The proposed legacy fix uses that same conservative
retry rule. Legacy grouping still uses upstream's priority: **ABORTED outranks
FAIL**, so skip plus failure produces ABORTED; failure remains in the comment.
This differs from local failure-first grouping and is retained for migration.

Use `python -m pip install pytest-xdist==3.8.0 pytest-rerunfailures==16.7`
for the tested optional parallel/retry plugins. Add `-n 2` to run on two workers,
or `--reruns=1` to retry once. Workers are separate processes; the main process
writes one report. Completion order is not guaranteed. `--dist=each` observations
of the same node are stored as separate worker attempts. Test phases and retries
are observations, not additional parametrized cases.

Local files include the pytest exit status and only observed reports, not a full
inventory of unexecuted tests. Collection errors and interruption produce partial
files when pytest reaches session finish. Worker crashes may lack parameter
metadata and Jira keys. Hard process termination may prevent any output.
Subtests, repeat plugins, crash recovery identity, cross-session merging and
per-iteration evidence are **not supported as distinct case models**. Do not
assume one record per subtest or one stable attempt ID across restarted workers.

**Proposed 0.1.0a2 hardening (not published):** requests have a 10-second connect and
60-second read-inactivity timeout (not a total deadline); redirects are rejected;
authentication and response shapes are checked; response bodies are not dumped
to shared temporary files. Failed publishing changes an otherwise successful
pytest exit to 3; existing nonzero exits are preserved. Uploads are withheld for
worker crashes, interrupted/collection-error sessions (including continue-on-error),
fail-fast/maxfail stops, or empty marked results.
Local Xray file writes are atomic and retain the previous file on failure.
These guarantees are **not in the published 0.1.0a1 wheel**.

## Troubleshooting and migration

| Symptom | Action |
| --- | --- |
| `unrecognized arguments` | Use `python -m pytest` from the activated environment; check `python -m pip show pytest-jira-xray-plus`. With plugin autoload disabled, explicitly load `-p pytest_xray.plugin`. |
| Duplicate plugin or import errors | Recreate the environment with only this fork, not upstream. |
| Duplicate Jira IDs | Add `--allow-duplicate-ids` only when intentionally grouping cases under one Test. |
| No `xray.json` | Both `--jira-xray` and `--xraypath` are required; case reporting is independent. |
| Cannot write local report | Create its parent directory, check permissions and choose different paths for each format. A failed atomic write leaves the previous file; do not mistake it for this run. |
| Missing environment variable | Set the variables for your chosen authentication mode; they are not read for file export. |
| HTTP 401/403 | Check the existing token and permissions with the sandbox administrator. Do not paste secrets into issue reports. |
| HTTP 404 or redirect | Check base URL, context path and Server/DC versus Cloud mode. |
| Certificate error | Configure the trusted CA bundle; do not disable verification to bypass it. |
| Timeout/invalid JSON/missing execution ID | Check server/proxy logs locally and whether the import already succeeded before retrying. |
| No native parameter rows in Jira | Expected: this implementation only emits aggregate status and optional comment text. |

From upstream, start a clean environment and replace the installed distribution
with `pytest-jira-xray-plus`. Imports, markers and the `xray` entry point remain
compatible. Review the narrower dependency baseline, explicitly enable case
reporting and comments as needed, and compare an offline `xray.json` first.
For alpha users, the proposed failure-exit, timeout and retry changes are intentional
behavior changes: update CI expectations before upgrading to a future release.

Advanced inherited hooks allow editing the final payload with `pytest_xray_results`
and attaching evidence through `pytest_runtest_makereport`; see the
[upstream-style reference](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/README.rst).
Hooks run trusted local Python and can alter the safety and correctness of a report.

## Try proposed 0.1.0a2 before publication

The PR's CI artifacts contain a wheel named
`pytest_jira_xray_plus-0.1.0a2-py3-none-any.whl` and source archive named
`pytest_jira_xray_plus-0.1.0a2.tar.gz`. In a fresh environment, install the downloaded
wheel with `python -m pip install /path/to/pytest_jira_xray_plus-0.1.0a2-py3-none-any.whl`.
This is an explicitly experimental local installation, not a PyPI release. The basic
example above works unchanged; the new options are available only in this build.

For a no-network size-policy demonstration after installing that wheel, run the
same `test_example.py` with:

```sh
python -m pytest -q test_example.py --jira-xray --xraypath=xray.json \
  --allow-duplicate-ids --xray-parameter-details --xray-comment-limit=256 \
  --xray-full-report=full-xray.json --xray-case-report=cases.json
```

With the original passing example, expect exit 0, two passing cases in
`cases.json`, one full comment in `full-xray.json`, and one shorter marked comment
in `xray.json`. The terminal reports one truncated comment. Neither file is sent.
The deliberately small 256-byte limit demonstrates the behavior, not a recommended
server setting.

## Development and stable-release gates

To test the proposed changes rather than the published alpha, clone this repository,
check out the reviewed commit, create a new environment, and run from the checkout:

```sh
python -m pip install -e . -r requirements-tests.txt build==1.6.1 setuptools==84.0.0 wheel==0.48.0 twine==7.0.0
python -m pytest -q
python tools/reproduce.py src --details
python tools/validate_offline.py
python tools/build_release.py release-dist
python -m twine check release-dist/*
```

Regression tests use synthetic data, blocked transport or a localhost fake server.
The [readiness record](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/RELEASE-READINESS.md)
separates executed checks from unverified claims. Before stable publication,
review CI, validate authorized sandbox comment behavior on 8.5.3-j10, confirm
Automatic's effective type and validate the configurable comment policy. Native iteration support
requires separate evidence for schema, stable identity, reordered/repeated imports
and persisted UI/readback; the
[experimental probe](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/QUICK-VALIDATION.md)
is a review plan, not an enabled feature. The
[minimal sandbox check](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/MINIMAL-SANDBOX-CHECK.md)
needs only synthetic Tests and an existing browser login; it requests no private
credentials or data. No workplace access is needed or requested.

Publishing remains manual through the existing `publish.yml` / `pypi` environment.
That workflow is prepared for 0.1.0a2 with the same manual approval, exact
artifact checks and permissions; it has not been dispatched. Review must finish
before merging or publishing. This work does not publish, create credentials, broaden permissions,
or relabel the alpha as stable. Report synthetic reproductions through
[GitHub issues](https://github.com/matusowskymichael/pytest-Jira-xray-plus/issues).
