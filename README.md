# pytest-Jira-xray-plus

Run your tests with pytest. Keep each input case in a local report. When you are
ready, send a summary and readable case details to Jira/Xray.

This tutorial takes you from two passing cases to an Xray-ready report using a
single file. **You can complete steps 1–7 without Jira or credentials.**

[Start the tutorial](#1-create-a-project) · [Send to Jira](#8-send-to-jira-optional) ·
[Options](#all-package-options) · [Troubleshooting](#troubleshooting-and-migration)

**What this package produces:** a local record for every observed pytest case,
and optionally one Xray result per Jira Test key. Parameter details can appear
in that result's **comment**. Native Xray iteration rows and datasets are not
supported.

This guide accompanies the **0.1.1 documentation patch**. Runtime behavior is
unchanged from 0.1.0. Until 0.1.1 is published, install 0.1.0 with the command below;
all tutorial features work in that release too.

## 1. Create a project

You need Python 3.12 or newer and a terminal. Start in a folder where you keep
small Python projects. These commands use Bash on Linux or macOS:

```sh
mkdir xray-demo
cd xray-demo
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install pytest-jira-xray-plus==0.1.0
```

Here is what each command does:

- `mkdir` creates the project folder; `cd` enters it.
- `python3.12 -m venv .venv` creates an isolated Python environment in `.venv`.
- Activating it makes `python` use that environment.
- `pip install` installs this package and its required dependencies, including pytest.

On Windows, create the environment with `py -3.12 -m venv .venv`. Activate it
with `.venv\Scripts\Activate.ps1` in PowerShell or
`.venv\Scripts\activate.bat` in Command Prompt. Use the same `python -m ...`
commands for the rest of the local tutorial.

**Use a fresh environment.** Do not also install `pytest-jira-xray`: that upstream
package and this fork share the `pytest_xray` module and `xray` plugin name.
Installing both can overwrite files. If that happened, recreate the environment.

No repository clone or configuration file is needed. Package installation needs
internet access; the local test commands below do not contact Jira.

## 2. Run two input cases

Create **`test_example.py`** inside `xray-demo`, next to `.venv`.
Paste this complete file:

<!-- tutorial:basic -->
```python
import pytest


@pytest.mark.parametrize(
    "value, expected",
    [(1, 2), (2, 3)],
    ids=["one-plus-one", "two-plus-one"],
)
def test_add_one(value, expected):
    assert value + 1 == expected
```

Run it from `xray-demo`:

<!-- run:basic -->
```sh
python -m pytest -q test_example.py
```

Expected summary (timing and progress characters may vary):

```text
2 passed
```

Here is how the file works:

- `import pytest` lets us use pytest's test decorators.
- The function name starts with `test_`, so pytest discovers it.
- `parametrize` runs the function once for each input pair: first `1, 2`, then
  `2, 3`. These two runs are called **cases**.
- `ids` gives those cases readable names. Use names without secrets.
- `assert` checks that adding one gives the expected result.

`python -m pytest` uses pytest from your active environment. `-q` keeps output
short. You have not added a Jira marker or contacted any server.

Your folder contains:

```text
xray-demo/
  .venv/
  test_example.py
```

Pytest may also create cache folders. You do not need to edit them.

## 3. Save that result locally

Keep the test file as it is. Add **one option** to the command:

<!-- run:local -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json
```

You still get `2 passed`. You also get **`cases.json`** in `xray-demo`.
The new option tells this plugin where to write its local report. It does not
enable Jira uploading.

Open the file in your editor, or pretty-print it:

<!-- run:inspect -->
```sh
python -m json.tool cases.json
```

Here is an excerpt from the report. It shows the actual case names and summaries;
we have left out each case's `attempts` list to keep this first view short:

<!-- json:local -->
```json
{
  "schema_version": 1,
  "pytest_exit_status": 0,
  "cases": [
    {
      "nodeid": "test_example.py::test_add_one[one-plus-one]",
      "status": "passed"
    },
    {
      "nodeid": "test_example.py::test_add_one[two-plus-one]",
      "status": "passed"
    }
  ]
}
```

`pytest_exit_status: 0` means the test session succeeded. A `nodeid` identifies the
file, function and input case. Each full case record also has an `attempts` list,
with observed phases:

| Phase | Meaning |
| --- | --- |
| `setup` | Prepare the test and any fixtures. |
| `call` | Run the test function. |
| `teardown` | Clean up after the test. |

A **fixture** is pytest code that prepares or cleans up a test resource. Our
example has no custom fixtures, but pytest still reports these phases.

`cases.json` is replaced on each run. Use a different filename to keep an older
run. Its parent folder must already exist. This file is the plugin's own format;
**it is not an Xray import file**.

## 4. Choose what the local report contains

By default, the report includes readable case IDs but excludes input values and
failure text. You can stop here and keep that default. The next two commands
show **alternative choices**, not options to combine.

To include scalar input values:

<!-- run:values -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json --xray-case-values
```

Expected: `2 passed`. Each attempt now has `parameter_values`, such as
`{"value": 1, "expected": 2}` for the first case. This is useful when the values are
safe to store; leave the option off otherwise.

To hide the function and parameter identities instead:

<!-- run:redact -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json --xray-case-redact-identities
```

Expected: `2 passed`. The case names become aliases such as `case-1`, and input
values remain absent. Aliases are assigned in arrival order and cannot be matched
across separate runs. This affects only the local JSON, not console output or
future Xray comments. It cannot be combined with `--xray-case-values`.

The following steps return to the default reporting command, so readable case IDs
will be present and values will be absent again.

## 5. See what happens when one case fails

Replace the file with this version. Only the second expected value has changed,
from `3` to `99`:

<!-- tutorial:failure -->
```python
import pytest


@pytest.mark.parametrize(
    "value, expected",
    [(1, 2), (2, 99)],
    ids=["one-plus-one", "two-plus-one"],
)
def test_add_one(value, expected):
    assert value + 1 == expected
```

<!-- run:failure -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json
```

Expected summary:

```text
1 failed, 1 passed
```

This is an intentional failure. Pytest exits with code **1**, rather than **0**
for success. The report is still written. `one-plus-one` remains `passed`;
`two-plus-one` is `failed`. Neither case disappears because another case has a
different result.

**Checkpoint:** you now have useful local reporting. You can apply
`--xray-case-report=cases.json` to your own pytest suite without adding Jira
markers or credentials. The remaining steps are optional.

## 6. Prepare an Xray result without uploading

Restore the passing inputs and add a Jira Test marker. Replace the whole file:

<!-- tutorial:xray -->
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

The new line, `@pytest.mark.xray("DEMO-1")`, associates both cases with one Jira
**Test** issue. `DEMO-1` is just a placeholder here; offline export does not look
it up. A **Test Execution** is the Jira issue that holds a set of test results.
A **Test Run** is the result of one Test inside that execution.

Keep the local report and add three options:

<!-- run:xray -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json --jira-xray --xraypath=xray.json --allow-duplicate-ids
```

| Addition | What it does |
| --- | --- |
| `--jira-xray` | Enables export of tests carrying the Xray marker. |
| `--xraypath=xray.json` | Writes the export to this file **instead of sending it**. |
| `--allow-duplicate-ids` | Allows the two cases to share `DEMO-1`; their Xray results are combined. |

Expected: `2 passed`, plus a message showing the generated Xray report file.
You now have two reports with different purposes:

| File | What you will find |
| --- | --- |
| `cases.json` | Two separate pytest cases, each passed. |
| `xray.json` | One Xray result for `DEMO-1`, with `status: "PASS"`. |

Why one Xray result? Both cases refer to the same Jira Test. This exporter combines
them under that key. It does not create native Xray iteration rows.

To keep readable input details in that combined result, add one more option:

<!-- run:comments -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json --jira-xray --xraypath=xray.json --allow-duplicate-ids --xray-parameter-details
```

Open `xray.json`. Its `comment` now contains both case names, scalar input
values, the reported phase and its outcome. Open `cases.json`: it still has two
separate records and still excludes input values by default.

`--xray-parameter-details` is an explicit opt-in because its comments can contain
sensitive values. It adds details only for parametrized tests. Without it,
passing cases usually have no comment text; failure details can still appear.

**Keep `--xraypath` in every offline export command.** Without it, `--jira-xray`
selects uploading. This also applies when options are inherited from `pytest.ini`
or `PYTEST_ADDOPTS`.

## 7. Keep full comments when an export is shortened

Large parametrized suites can produce long comments. The default client policy
limits each exported comment to **32,000 UTF-8 bytes**. This is a configurable
client choice, not a universal Jira/Xray server limit.

To see the behavior with our small example, deliberately choose a tiny limit:

<!-- run:archive -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json --jira-xray --xraypath=xray.json --allow-duplicate-ids --xray-parameter-details --xray-comment-limit=256 --xray-full-report=full-xray.json
```

Two new options work together:

- `--xray-comment-limit=256` bounds each final exported comment to 256 UTF-8
  bytes, including the truncation notice. It does not limit the entire request
  or attached evidence. The minimum is 256.
- `--xray-full-report=full-xray.json` saves the **complete original Xray
  payload** before any comment is shortened.

Expected: `2 passed` and a message containing `truncated 1 comment(s)`.

| File | Result |
| --- | --- |
| `cases.json` | Both structured cases, unaffected by the comment limit. |
| `full-xray.json` | Full original comment containing both case identities and values. |
| `xray.json` | Shortened comment with an explicit `TRUNCATED` notice. |

If an oversized comment has no full-report path, export stops instead of silently
losing text. If the archive cannot be written, export also stops. An otherwise
passing pytest session then exits with code 3. Statuses and evidence are not
truncated. Use the default limit for ordinary evaluation, then validate the
appropriate size with your server administrator.

The full archive can contain values, failure text and evidence. Protect it like
test data. All three report paths must differ. Files are replaced on each run;
choose unique paths to retain history.

## 8. Send to Jira (optional)

Everything above was local. This step sends a request to a server. Start with an
authorized disposable test project and existing credentials; no credentials or
private test data need to be shared with the maintainer.

### Prepare the two issue keys

1. Choose an existing sandbox Jira **Test** issue. Replace `DEMO-1` in the marker
   with its key.
2. Choose an existing sandbox **Test Execution**, for example `DEMO-100`.
   You will pass that key as `--execution`.
3. Rerun the offline command from step 6 and inspect `xray.json`. Confirm that it
   names the intended Test and contains only information you intend to send.

The two keys are not interchangeable: one identifies the Test; the other selects
where its result goes.

### Configure Server or Data Center authentication

This example uses an existing personal access token and **Bash**. It reads the
token without placing it in shell history:

```bash
export XRAY_API_BASE_URL='https://jira.example.invalid'
read -r -s -p 'Existing sandbox Jira token: ' XRAY_API_KEY
printf '\n'
export XRAY_API_KEY
```

Replace the `.invalid` URL with the authorized sandbox base URL. Include Jira's
context path, if it has one, but do not append a REST endpoint. The plugin adds
`/rest/raven/2.0/import/execution` itself.

`XRAY_API_BASE_URL` tells the plugin where Jira is. `XRAY_API_KEY` holds the token;
`--api-key-auth` below selects that authentication method. In CI, inject these
through protected environment variables rather than committing them to files.

### Upload the result

Use the same passing test file. This time **remove `--xraypath`**:

```sh
python -m pytest -q test_example.py --jira-xray --api-key-auth --execution=DEMO-100 --allow-duplicate-ids --xray-parameter-details --xray-case-report=cases.json --xray-full-report=full-xray.json
```

Replace `DEMO-100` with your chosen execution key. The new options select token
authentication and an existing Test Execution. Keep `--cloud` **off** for
Server/Data Center.

On successful import, pytest prints the returned Test Execution ID. In Jira, open
that Test Execution and the Test Run for your Test. Expect one aggregate result
and comment text with case details, not native per-input iteration rows.
The two local report files remain available for inspection.

When finished with this Bash session:

```bash
unset XRAY_API_KEY
```

Omitting `--execution` asks Xray to create a new Test Execution, subject to its
required fields and permissions. Start with an explicit disposable execution so
you know what is being updated. Reimports can replace existing Test Run details,
including dataset/iteration information; inspect a run before retrying a timeout.
Imports are not retried automatically because the server might already have
accepted the first request. This replacement behavior is documented in the
[official Server/DC import API](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301667997).

This command uses the aggregate comment fallback. Confirm the effective Test type
with your administrator if your project uses a custom label such as **Automatic**.
A label alone does not establish Generic behavior or native iteration support.
See the compatibility section below for the tested versions and limits.

## Optional recipes

Scalar values are strings, integers, finite floats, booleans or `None`. Other
values get a placeholder instead of invoking arbitrary object serialization.
Indirect fixtures record their input parameters, not the fixture's return value.
Use step 4 to choose values or identity aliases for the local report.

### Parallel tests and retries

Install the optional plugins separately:

```sh
python -m pip install pytest-xdist==3.8.0 pytest-rerunfailures==16.7
```

<!-- run:parallel -->
```sh
python -m pytest -q test_example.py -n 2 --xray-case-report=cases.json
```

<!-- run:retries -->
```sh
python -m pytest -q test_example.py --reruns=1 --xray-case-report=cases.json
```

`-n 2` uses two worker processes. `--reruns=1` allows one retry after a failure.
Our restored passing example has nothing to retry. With a failing-then-passing
test, pytest may exit 0 while this reporter still records an earlier failure;
see the status table below. The main process writes one report. Results can arrive
in a different order. With `--dist=each`, the same node observed on two workers
is retained as two worker attempts.

### Associate one function with multiple Tests

Replace the marker in step 6 with `@pytest.mark.xray("DEMO-1", "DEMO-2")`.
Each marked Test receives the combined result. Use this only when those Test
issues are genuinely intended to share the result.

## Authentication and execution settings

Choose one authentication method:

| Method | CLI option | Required environment variables |
| --- | --- | --- |
| Jira personal access token | `--api-key-auth` | `XRAY_API_BASE_URL`, `XRAY_API_KEY` |
| Basic authentication, if enabled by your administrator | Neither auth flag | `XRAY_API_BASE_URL`, `XRAY_API_USER`, `XRAY_API_PASSWORD` |
| Xray Cloud client credentials | `--cloud --client-secret-auth` | `XRAY_API_BASE_URL`, `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` |

Cloud is a different service. It uses the Xray API base URL, `/api/v2/authenticate`
and `/api/v2/import/execution`, with `PASSED`/`FAILED` status spelling. Server/DC
uses `PASS`/`FAIL`. `--cloud` does not enable native iterations or change Test types.
Cloud has synthetic test coverage, not live target validation.

TLS certificate verification is enabled by default. Set `XRAY_API_VERIFY_SSL`
to `True` or to a trusted CA bundle path for an internal CA. `False` disables
verification and should not be used with real credentials.

Optional execution metadata:

| Environment variable | Meaning |
| --- | --- |
| `XRAY_EXECUTION_SUMMARY` | Execution title. A new execution defaults to `Execution of automated tests`. |
| `XRAY_EXECUTION_DESC` | Execution description. |
| `XRAY_EXECUTION_REVISION` | Revision, such as a commit ID. |
| `XRAY_EXECUTION_TEST_ENVIRONMENTS` | Environment names separated by whitespace. |
| `XRAY_EXECUTION_FIX_VERSION` | Fix version; the first nonempty parsed value is used. |

These variables configure the legacy exporter; local case reporting does not
need them. Secrets belong in your shell environment or protected CI settings,
not test files or command-line arguments.

## All package options

All on/off switches below default to off. Paths and issue keys are text values
and default to unset; `--xray-comment-limit` is an integer defaulting to 32000.
The table describes the combinations required to make each option useful.

| Option | Effect |
| --- | --- |
| `--xray-case-report=PATH` | Write observed cases locally. Parent folder must exist. No Jira required. |
| `--xray-case-values` | Include scalar input values in the case report; requires its path. |
| `--xray-case-redact-identities` | Replace local names/IDs with per-run aliases; requires the case report and excludes case values. |
| `--jira-xray` | Enable export of marked tests. Uploads unless `--xraypath` is set. |
| `--xraypath=PATH` | With `--jira-xray`, write Xray JSON instead of uploading. Creates parent folders. |
| `--allow-duplicate-ids` | Combine cases that share a Jira Test key. |
| `--xray-parameter-details` | Add parameter identities and scalar values to legacy comments. |
| `--xray-comment-limit=BYTES` | Maximum UTF-8 bytes per final comment; default 32000, minimum 256. |
| `--xray-full-report=PATH` | Archive the complete original legacy payload before shortening comments; requires `--jira-xray`. |
| `--execution=KEY` | Update an existing Test Execution. |
| `--testplan=KEY` | Set a Test Plan key in execution metadata. |
| `--api-key-auth` | Authenticate using `XRAY_API_KEY` as a Bearer token. |
| `--client-secret-auth` | Authenticate with Xray Cloud client credentials. |
| `--cloud` | Use the Cloud import endpoint and status spelling. |
| `--add-captures` | Add captured stdout, stderr and logs to comments; may expose secrets. |

Use `python -m pytest --help` for pytest's own options. `--collect-only` does not
write reports. No option enables native iteration rows.

## Result rules and compatibility

| Event | Local case summary | Legacy Xray summary |
| --- | --- | --- |
| Passing call | passed | PASS |
| Failed call or fixture setup/teardown | failed | FAIL |
| Skip | skipped | ABORTED |
| Expected failure (`xfail`) | skipped; xfail recorded | FAIL |
| Unexpected pass (`xpass`) | passed; xpass recorded | PASS |
| Strict unexpected pass | failed | FAIL |
| Failed attempt then successful retry | failed; both attempts retained | FAIL |

The local report preserves any earlier failure. Legacy grouping retains upstream's
priority: **ABORTED outranks FAIL**. A group containing a skip and failure therefore
has ABORTED status, with failure information in comments. This differs from local
failure-first grouping. Statuses are not interchangeable with pytest's exit code.

Publishing failure changes an otherwise successful pytest exit to 3; an existing
nonzero exit is preserved. Remote imports are withheld after worker crashes,
fail-fast/maxfail stops, collection failures (including continue-on-error),
interruptions, or when there are no marked results. Local files can still contain
partial observations. Reports list observed results, not an inventory of tests
that never ran. Hard process termination can prevent any final file from being written.

Requests use a 10-second connect timeout and a 60-second read-inactivity timeout,
not a total deadline. Redirects are rejected. Authentication and response shapes
are checked. The plugin does not dump raw server responses to shared temporary files.
Local file replacement is atomic; failed writes retain any prior report.

Python metadata requires `>=3.12`, pytest `>=9.1.1,<10` and requests `>=2.34.2,<3`.
CI checks Linux on Python 3.12, 3.13 and 3.14; the tested baseline uses pytest 9.1.1,
requests 2.34.2, xdist 3.8.0 and rerunfailures 16.7. Windows/macOS instructions
are provided but those platforms have not been executed in this validation.
Future dependency versions are not automatically certified.

Subtests and repeat plugins are not supported as distinct case models. Reliable
case identity across worker crashes/restarts, cross-session aggregation and
per-iteration evidence are outside this release. Crashed-worker reports can lack
parameter metadata or Jira keys. Native rows and datasets are unsupported even
when a Test type's label is Automatic.

## Troubleshooting and migration

| What happened | What to do |
| --- | --- |
| `unrecognized arguments` | Activate the intended environment and use `python -m pytest`. Check `python -m pip show pytest-jira-xray-plus`. If plugin autoload is disabled, add `-p pytest_xray.plugin`. |
| Duplicate plugin/import errors | Create a fresh environment with this fork only, not upstream `pytest-jira-xray`. |
| Duplicate Jira IDs | Add `--allow-duplicate-ids` only when the cases intentionally share one Test. |
| No `xray.json` | Use both `--jira-xray` and `--xraypath=xray.json`. Case reporting is separate. |
| Cannot write a report | Check permissions and distinct paths. Create the case-report parent folder. A previous file retained after failure is not a new result. |
| Comment exceeds the limit | Add `--xray-full-report=PATH` to retain full text before truncation; inspect the resulting export. |
| Missing authentication variable | Set the variables for your selected auth method. Offline file exports do not need credentials. |
| HTTP 401/403 | Check existing credentials and permissions with the sandbox administrator. Do not paste secrets into issue reports. |
| HTTP 404 or redirect | Check the base URL, context path and Server/DC versus Cloud mode. |
| Certificate error | Configure the trusted CA bundle; do not bypass verification. |
| Timeout, invalid JSON or missing execution ID | Inspect local server/proxy information and check whether the import already succeeded before retrying. |
| No native parameter rows | Expected: this exporter provides aggregate status and optional comment detail, not native iterations. |

**From upstream:** create a fresh environment and install `pytest-jira-xray-plus`.
The Python imports, marker and `xray` plugin name are retained. Check the dependency
requirements, add local reporting as needed, and compare an offline export before
uploading. Do not install both distributions together.

**From 0.1.0:** 0.1.1 is a documentation patch with unchanged runtime behavior.
**From 0.1.0a1:** later releases add bounded comments, meaningful publishing failures,
atomic file export and failure-preserving rerun summaries; update CI expectations.

## Advanced: customize the export with hooks

A hook is a Python function pytest calls at a particular point in a run. You do
not need one for the tutorial. If you need custom execution metadata or evidence,
create **`conftest.py`** beside `test_example.py`:

<!-- tutorial:hooks -->
```python
import pytest
from pytest_xray import evidence


def pytest_xray_results(results, session):
    results["info"]["revision"] = "tutorial-revision"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        report.evidences = getattr(report, "evidences", []) + [
            evidence.text(data="synthetic evidence", filename="example.txt")
        ]
```

<!-- run:hooks -->
```sh
python -m pytest -q test_example.py --jira-xray --xraypath=xray.json --allow-duplicate-ids --xray-parameter-details
```

Expected: `2 passed`. `xray.json` contains `info.revision: "tutorial-revision"`
and two evidence entries, one per case, on the combined Test result. The evidence
text is encoded in the payload. These are Test Run attachments, not per-iteration
attachments. `cases.json` is not written by this command.

`pytest_xray_results` edits the final legacy payload before archival and comment
bounds are applied. The report hook attaches evidence after pytest creates each
call report. Hooks execute trusted local Python and can change correctness or
expose data; use only the fields and content you intend to export. Delete this
optional `conftest.py` when finished with the example.

## Project and development

This is an independent Apache-2.0 fork of
[pytest-jira-xray](https://github.com/fundakol/pytest-jira-xray), based on
`6ac1117585da590001cdbc2bf261b78683c19dcb` (upstream's 0.9.4 line).
Report issues with synthetic examples through
[GitHub issues](https://github.com/matusowskymichael/pytest-Jira-xray-plus/issues).

From a checkout in a fresh environment:

```sh
python -m pip install -e . -r requirements-tests.txt build==1.6.1 setuptools==84.0.0 wheel==0.48.0 twine==7.0.0
python -m pytest -q
python tools/reproduce.py src --details
python tools/validate_offline.py
python tools/build_release.py release-dist
python -m twine check release-dist/*
```

Tests use synthetic data, blocked transport or a localhost fake service.
[Release evidence](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/RELEASE-READINESS.md)
distinguishes independent checks from user-reported validation.
The [sandbox capability procedure](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/MINIMAL-SANDBOX-CHECK.md)
is optional research, not implemented native support. It requests no private data.
Publishing uses the existing manual workflow, reviewed commit and artifact hashes.
