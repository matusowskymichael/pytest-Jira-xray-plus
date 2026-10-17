# pytest-Jira-xray-plus

[![PyPI version snapshot](https://matusowskymichael.github.io/pytest-Jira-xray-plus/status/pypi.svg)](https://pypi.org/project/pytest-jira-xray-plus/)
[![Tested Python versions](https://matusowskymichael.github.io/pytest-Jira-xray-plus/status/python.svg)](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/workflows/tests.yml)
[![Licence](https://matusowskymichael.github.io/pytest-Jira-xray-plus/status/license.svg)](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/LICENSE)
[![Tests](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/workflows/tests.yml/badge.svg?branch=main&event=push)](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/workflows/tests.yml)
[![Documentation build](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/workflows/docs.yml/badge.svg?branch=main&event=push)](https://matusowskymichael.github.io/pytest-Jira-xray-plus/)
[![Measured plugin line coverage](https://matusowskymichael.github.io/pytest-Jira-xray-plus/coverage/coverage.svg)](https://matusowskymichael.github.io/pytest-Jira-xray-plus/coverage/)

Integrate pytest with **Jira and the Xray test management app for Jira**. Associate
pytest tests with Jira Test issues, run parametrized cases, and publish their
aggregate results into an Xray Test Execution. **Jira with Xray is required for
the intended integration.**

[Integration quick start](https://matusowskymichael.github.io/pytest-Jira-xray-plus/tutorial/install/)
· [Prerequisites](#jiraxray-prerequisites) · [Upload results](#4-authenticate-and-publish-to-jiraxray)
· [Options](#all-package-options) · [Troubleshooting](#troubleshooting-and-migration)

This guide maps two pytest cases to one existing Jira Test and publishes one
aggregate Test Run. Parameter details can be included in its **comment** by
explicit opt-in. Native Xray iteration rows and datasets are not supported.
Offline Xray JSON is a preview before import; local case JSON and full-comment
archives provide debugging and audit records for the integration.

This guide covers **0.1.7 collection validation and lookup improvements**, retaining Generic as the target
Xray Test type. The examples also work with 0.1.2 and 0.1.3; the multi-key attachment
isolation fix requires 0.1.4 or later. Installation selects the latest published
version; check the [PyPI release history](https://pypi.org/project/pytest-jira-xray-plus/#history)
for availability.
Offline previews still require neither network access nor credentials.

## Jira/Xray prerequisites

- A Jira Server/Data Center instance with the Xray app and permission to import
  test results. The requested target is **Xray 8.5.3-j10**; this exact server/version
  has not been independently validated. The implemented transport uses Xray's
  Server/DC `/rest/raven/2.0/import/execution` API. Keep `--cloud` off for this target.
- An existing **Generic Test** issue and **Test Execution** in an authorized project.
  This guide uses `DEMO-1` and `DEMO-100` as placeholders; replace them with your
  own keys before uploading. A Test identifies what is tested; the Execution
  holds its result. Both input cases share the Test key and produce one Test Run.
- **Generic** is the confirmed target Xray Test type. Use an existing Generic
  Test; the plugin imports results by issue key and does not create, select or
  change the Test type. This confirmation does not establish native iteration support.
- An existing Jira personal access token (or administrator-enabled Basic auth),
  the Jira base URL including any context path, and a trusted TLS certificate/CA.
  Step 4 configures these through environment variables; never put secrets in tests.
- Python 3.12+ and pytest 9.1.1–9.x. Use a fresh environment containing this fork
  only; upstream `pytest-jira-xray` installs the same module and plugin name.

Use an authorized disposable Test Execution for first validation. Confirm its
aggregate result and comments in Jira before using this configuration in production.
The preview commands deliberately perform no network requests and do not validate
credentials, issue existence, permissions or server-side import behavior.

## 1. Create a project

First confirm the Jira/Xray prerequisites above. In a terminal, start in a folder
where you keep small Python projects. These commands use Bash on Linux or macOS:

```sh
mkdir xray-demo
cd xray-demo
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install pytest-jira-xray-plus
```

Here is what each command does:

- `mkdir` creates the project folder; `cd` enters it.
- `python3.12 -m venv .venv` creates an isolated Python environment in `.venv`.
- Activating it makes `python` use that environment.
- `pip install` installs this package and its required dependencies, including pytest.

On Windows, create the environment with `py -3.12 -m venv .venv`. Activate it
with `.venv\Scripts\Activate.ps1` in PowerShell or
`.venv\Scripts\activate.bat` in Command Prompt. Use the same `python -m ...`
commands for the rest of the integration tutorial.

**Use a fresh environment.** Do not also install `pytest-jira-xray`: that upstream
package and this fork share the `pytest_xray` module and `xray` plugin name.
Installing both can overwrite files. If that happened, recreate the environment.

No repository clone or configuration file is needed. Package installation needs
internet access; the local test commands below do not contact Jira.


## 2. Run two input cases

Map the example to your Jira Test (`DEMO-1` is a placeholder). Create **`test_example.py`** inside `xray-demo`, next to `.venv`.
Paste this complete file:

<!-- tutorial:basic -->
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
- `@pytest.mark.xray("DEMO-1")` maps both cases to the existing Jira Test.
- `parametrize` runs the function once for each input pair: first `1, 2`, then
  `2, 3`. These two runs are called **cases**.
- `ids` gives those cases readable names. Use names without secrets.
- `assert` checks that adding one gives the expected result.

`python -m pytest` uses pytest from your active environment. `-q` keeps output
short. This first command checks the test itself. The Jira marker is in place,
but uploading starts only when `--jira-xray` is enabled without `--xraypath`.

Your folder contains:

```text
xray-demo/
  .venv/
  test_example.py
```

Pytest may also create cache folders. You do not need to edit them.


## 3. Preview the Jira/Xray import

Before importing results, review the Xray payload. Keep the passing test and
its Jira Test marker; here is the complete file:

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

The marker, `@pytest.mark.xray("DEMO-1")`, associates both cases with one Jira
**Test** issue. `DEMO-1` is just a placeholder here; offline export does not look
it up. A **Test Execution** is the Jira issue that holds a set of test results.
A **Test Run** is the result of one Test inside that execution.

Generate the Xray preview and a case audit report:

<!-- run:xray -->
```sh
python -m pytest -q test_example.py --xray-case-report=cases.json --jira-xray --xraypath=xray.json --allow-duplicate-ids
```

| Addition | What it does |
| --- | --- |
| `--jira-xray` | Enables export of tests carrying the Xray marker. |
| `--xraypath=xray.json` | Writes the export to this file **instead of sending it**. |
| `--allow-duplicate-ids` | Allows the two cases to share `DEMO-1`; their Xray results are combined. |

Use `--allow-duplicate-ids` only when separate pytest cases intentionally map to
one existing Jira Test. Without it, collection stops at the first test item that
reuses a key; the diagnostic lists that item's duplicates in marker order.
Repeating a key within one marker is deduplicated and does not create another
Xray result. Even with the flag, malformed markers are still rejected.

The 0.1.7 collection optimization replaces growing-list scans with set
membership. These commands and grouping rules are unchanged; it does not add
native iterations or change Jira/Xray configuration. For a deterministic developer
benchmark from a checkout with development dependencies installed, run
`python tools/benchmark_collection.py`. It compares key-operation counts against
the 0.1.6 list algorithm, not total pytest time or live server performance.

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


## 4. Authenticate and publish to Jira/Xray

Publish the reviewed result into Jira/Xray. This step makes the integration
request; the preceding payload preview did not contact the server. Start with an
authorized disposable test project and existing credentials; no credentials or
private test data need to be shared with the maintainer.

### Prepare the two issue keys

1. Choose an existing sandbox Jira **Generic Test** issue. Replace `DEMO-1` in the marker
   with its key.
2. Choose an existing sandbox **Test Execution**, for example `DEMO-100`.
   You will pass that key as `--execution`.
3. Preview the intended upload with the command below. Replace `DEMO-100` with
   your chosen execution key. Keep `--xraypath=xray.json`: this preview is local.

<!-- run:preupload -->
```sh
python -m pytest -q test_example.py --jira-xray --execution=DEMO-100 --allow-duplicate-ids --xray-parameter-details --xray-case-report=cases.json --xray-full-report=full-xray.json --xraypath=xray.json
```

<!-- run:inspect_xray -->
```sh
python -m json.tool xray.json
```

Expect `2 passed`. Check `testExecutionKey` matches the intended execution,
`tests[0].testKey` matches your Test marker, and `comment` contains the case details
you intend to send. This uses the normal comment limit, not the archive recipe's deliberately
small demonstration limit. No credentials are required for this file export.

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

This command targets an existing **Generic Test** using the aggregate comment
fallback. It does not set or change the Test type, and Generic targeting does not
enable native iteration rows or datasets.
See the compatibility section below for the tested versions and limits.


## 5. Audit cases behind a Jira Test Run

Use `cases.json` to investigate the pytest cases behind an aggregate Jira Test
Run. Keep the same marked test file. To reproduce only the local observations
while debugging an integration result, run:

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


## 6. Choose audit report contents

By default, the report includes readable case IDs but excludes input values and
failure text. Keep that default unless your integration audit requires more detail. The next two commands
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


## 7. Diagnose a failing case

Replace the file with this version. Only the second expected value has changed,
from `3` to `99`:

<!-- tutorial:failure -->
```python
import pytest


@pytest.mark.xray("DEMO-1")
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

**Checkpoint:** the audit report retains both input cases behind the Jira Test.
This diagnostic run has not updated Jira. Restore passing inputs before the next
recipe, and repeat the preview/upload workflow when you intend to update Xray.


## 8. Archive complete Xray comments
Restore the passing, marked test before trying this archive recipe:

<!-- tutorial:restore -->
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


## Optional recipes

Scalar values are strings, integers, finite floats, booleans or `None`. Other
values get a placeholder instead of invoking arbitrary object serialization.
Indirect fixtures record their input parameters, not the fixture's return value.
Use step 6 to choose values or identity aliases for the local report.

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

Replace the marker in step 3 with `@pytest.mark.xray("DEMO-1", "DEMO-2")`.
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
| `--xray-case-report=PATH` | Write observed cases locally. Parent folder must exist. Audit/debug output; does not upload. |
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
The unreleased cleanup fix preserves the original write error if removing its
temporary file also fails. That diagnostic includes the temporary path and cleanup
error; the file may contain report data. After the run, inspect that specific path
and remove it when permissions allow. Do not treat an older retained report as a
new result. Published 0.1.7 can instead surface the secondary cleanup exception.

Python metadata requires `>=3.12`, pytest `>=9.1.1,<10` and requests `>=2.34.2,<3`.
CI checks Linux on Python 3.12, 3.13 and 3.14; the tested baseline uses pytest 9.1.1,
requests 2.34.2, xdist 3.8.0 and rerunfailures 16.7. Windows/macOS instructions
are provided but those platforms have not been executed in this validation.
Future dependency versions are not automatically certified.

Subtests and repeat plugins are not supported as distinct case models. Reliable
case identity across worker crashes/restarts, cross-session aggregation and
per-iteration evidence are outside this release. Crashed-worker reports can lack
parameter metadata or Jira keys. Native rows and datasets are unsupported
for the confirmed Generic target.


## Troubleshooting and migration

**Duplicate Test keys (0.1.7+):** if separate pytest cases intentionally
map to one existing Jira Test, add `--allow-duplicate-ids` to the same preview or
upload command. Otherwise give the cases their correct distinct Test keys.
Do not add the flag just to hide an accidental mapping mistake. Repeating a key
within one marker remains harmless and is deduplicated.

Without that flag, the diagnostic still lists duplicates from the first offending
item in marker order. Version 0.1.7 reports this as a collection error,
not `INTERNALERROR`, in serial and xdist. No test fixtures run, and no upload is
attempted, including with `--continue-on-collection-errors`. An offline preview
can contain an empty `tests` list. Fix the mapping or intentionally enable grouping,
then rerun the tutorial's offline preview before uploading.

CI scripts should treat every nonzero pytest exit as a failed run: duplicate-policy
violations now use pytest's collection-failure classification (typically exit 2
in serial, or exit 1 with xdist/continue-on-collection-errors), rather than the old
internal-error exit 3. Normal pytest/local-case-only runs and `--collect-only` keep
their existing behavior. Version 0.1.6 and earlier do not contain this fix.

**Invalid Test-key marker (0.1.7+):** use nonempty strings, for example
`@pytest.mark.xray("DEMO-1")`, `@pytest.mark.xray("DEMO-1", "DEMO-2")`, or
`@pytest.mark.xray(["DEMO-1", "DEMO-2"])`. Do not omit the arguments or pass
empty/whitespace-only strings, an empty list, `None`, numbers, or other objects.
Keys retain their supplied spelling and order; there is no new Jira-key regex.
Repeating a key in one marker is still deduplicated. Separate cases sharing a key
still require `--allow-duplicate-ids`.

With this fix, malformed Test keys produce a normal collection error before any
test fixtures run when `--jira-xray` is enabled. This also works with xdist and
`--continue-on-collection-errors`: no tests execute and uploads are withheld;
an offline `--xraypath` preview can contain an empty `tests` list. Correct the
marker, then rerun the same offline preview command from the tutorial before
uploading. Without `--jira-xray`, ordinary pytest and local-case reports keep
working without validating Xray markers. `--collect-only` still only lists tests.
Version 0.1.6 and earlier can instead show `INTERNALERROR` for these malformed
markers. It does not check whether Jira keys exist
or validate credentials, and it does not change the duplicate-key diagnostic text.

**Invalid `defects` marker (0.1.5+):** when `--jira-xray` is enabled, `defects`
must be a list of nonempty strings. For example, change the marker on your test to:

```python
@pytest.mark.xray("DEMO-1", defects=["BUG-1", "BUG-2"])
```

Use `defects=[]` or omit it when there are no defects. Do not pass a bare string
(`defects="BUG-1"`), tuple, `None`, numbers, empty strings or whitespace-only
strings. Values are not trimmed or checked against a Jira-key regex; Jira/Xray
still determines whether a supplied key exists and is usable.

Run the same offline preview command from the tutorial. Malformed defects now
produce a collection error before **any test fixtures run**, in serial and xdist.
Uploads are withheld, even with `--continue-on-collection-errors`; a local preview
may contain an empty `tests` list for diagnosis. The error describes the required
shape without displaying defect values. Fix the marker and rerun. Ordinary pytest
runs and local-case reporting without `--jira-xray` do not apply this validation.
`--collect-only` retains its existing behavior of not configuring Xray reporting;
it lists tests but does not validate these markers, run fixtures or upload.
This validates marker configuration only; it does not contact Jira or validate
credentials. Earlier versions could fail later inside report hooks or retain
invalid values in export payloads.


| What happened | What to do |
| --- | --- |
| `unrecognized arguments` | Activate the intended environment and use `python -m pytest`. Check `python -m pip show pytest-jira-xray-plus`. If plugin autoload is disabled, add `-p pytest_xray.plugin`. |
| Duplicate plugin/import errors | Create a fresh environment with this fork only, not upstream `pytest-jira-xray`. |
| Duplicate Jira IDs | Add `--allow-duplicate-ids` only when the cases intentionally share one Test. |
| No `xray.json` | Use both `--jira-xray` and `--xraypath=xray.json`. Case reporting is separate. |
| Cannot write a report | Check permissions and distinct paths. Create the case-report parent folder. A previous file retained after failure is not a new result. With the unreleased cleanup fix, inspect the named temporary file if removal also failed; it may contain report data. Remove only that file after the run when permissions allow. |
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

**From 0.1.0–0.1.2:** 0.1.3 confirms Generic as the target Test type in the
documentation; runtime behavior is unchanged.
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

When a case maps to multiple Jira Test keys, each key keeps its own evidence and
defect lists. For example, case 1 mapped to `SYN-1` and `SYN-2` with `BUG-1`, followed
by case 2 mapped only to `SYN-1` with `BUG-2`, gives `SYN-1` both cases' attachments
and defects; `SYN-2` receives only case 1's. Two parameter cases both mapped to both
keys produce two attachment occurrences per key, even when their filenames and
contents are identical. Defect identifiers are still de-duplicated per key.

Version 0.1.4 fixes list sharing that could leak later attachments/defects into an
unrelated key or inflate attachment counts. It changes neither status precedence
nor comments, and needs no new flags. Use `--allow-duplicate-ids` when multiple
cases reuse a key. The fix applies to serial and xdist file exports and the same
payload used for upload; live server behavior has not been revalidated.

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


Version tagging adds `vX.Y.Z` and a matching GitHub Release after a verified
PyPI publication, with the exact published wheel and source archive. The approved
workflow is enabled; the 0.1.5 backfill and no-op retry were verified. Maintainers:
see [tagged release setup and retry instructions](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/RELEASING.md).
Package installation and Jira/Xray configuration are unchanged.


The coverage badge is a measured **snapshot of plugin executable lines** in
`src/pytest_xray`, from the full synthetic test suite including Python subprocesses.
Its linked report identifies the exact commit, measurement time and line/branch
counts; it can lag main and is not a live Xray compatibility claim. Tests and
repository tools are outside this denominator. Python badges describe the tested
3.12–3.14 matrix; installation requires Python 3.12+. See
[coverage scope and report updates](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/COVERAGE.md).

Version, tested Python and licence images are first-party [metadata snapshots](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/gh-pages/status/metadata.json), refreshed after releases.
The test and documentation images show live main-branch workflow status.
