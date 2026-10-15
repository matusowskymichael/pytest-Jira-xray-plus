# Try it in two stages

The implemented feature is **local case JSON and optional Xray comments**.
It does not emit proven native iterations. Stage 1 needs no Jira. Stage 2 is an
optional, experimental capability probe for a disposable Xray 8.5.3-j10 sandbox;
it is not a working integration recipe or a prerequisite for trying the package.

## 1. One-command offline demonstration

From this checkout, install in a fresh environment (do not co-install upstream):

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python tools/validate_offline.py
```

On Windows activate with `.venv\Scripts\activate` instead. Installation may
access PyPI; the demo itself runs locally with HTTP and socket connections
blocked, external pytest plugin autoload disabled and no Jira configuration.
It creates the following synthetic test in a temporary directory and runs both
orders, first `[0, 1]`, then `[1, 0]`:

```python
@pytest.mark.xray('SYN-1')
@pytest.mark.parametrize('value', [0, 1], ids=['case-a', 'case-b'])
def test_demo(value):
    assert value == 1
```

In the reversed run the IDs still follow their values: case-a always fails,
case-b always passes. Expected console output:

```text
forward: case-a=failed, case-b=passed; pytest_exit_status=1; Xray JSON status=FAIL
reverse: case-a=failed, case-b=passed; pytest_exit_status=1; Xray JSON status=FAIL
PASS: both cases retained in both orders; comments retained; no Jira request made.
Native iterations: NOT tested. Temporary reports removed.
```

The demo exits 0 only after checking both intentionally failing pytest runs
(exit 1), two separate case records/attempts, omitted parameter values in the
local case report, and both case names in the legacy Xray JSON comment. The
legacy JSON aggregate remains FAIL in both orders. This does not prove server
aggregation: the submitted summary itself is explicitly FAIL.

To keep a report for inspection, use the existing synthetic example:

```sh
python -m pytest examples/synthetic.py --xray-case-report=cases.json
```

Expect exit 1 and `cases.json` containing two case records with `failed` and
`passed`, each with setup/call/teardown observations. IDs in this example are
`first-fails` and `last-passes`. Do not import `cases.json` into Xray: it is our
local schema. See [schema details](CASE-REPORT.md).

## 2. Optional sandbox probe: review only by default

**Nothing here sends requests.** The two static files
[forward.json](../examples/native-probe/forward.json) and
[reverse.json](../examples/native-probe/reverse.json) are dry-run review inputs.
They have never been sent to Jira. Do not use a workplace project or valuable
execution. No credential, screenshot or real test is needed for this kit.

Before any manual import, confirm with the sandbox administrator or vendor:

- Exact build is 8.5.3-j10. In **Jira Administration → Manage apps → Xray →
  Manage Test Types**, check the effective project context's **Type** column.
  A custom label such as **Automatic** must actually map to Generic/Unstructured.
  A label alone is insufficient. Do not change the type to make this probe pass.
- The supported JSON schema for that build accepts status-only `iterations` on
  this kind. Current Server/DC documentation is not a pinned 8.5.3 contract.
- The sandbox's PASS and FAIL status names exist. If schema or type support is
  unresolved, stop at review and ask the support question below.

If explicitly choosing to proceed in a disposable sandbox:

1. Create one dummy Generic Test with a synthetic definition, and one disposable
   Test Execution. Add only that Test to the execution. Keep any environment
   selection consistent. Record their keys locally.
2. Copy both JSON files outside the checkout and replace `SYN-1` and `SYN-100`
   with those two sandbox keys. Check both references before importing. Each
   file supplies the complete two-row result for one Test Run; never import one
   case at a time. There are no Manual-only parameters or datasets.
3. Open that disposable **Test Execution**, choose **Import Execution Results**,
   choose **Xray JSON**, select your edited forward file and import. If this UI
   action/format is unavailable, stop and ask the administrator; do not guess
   REST endpoints or create credentials as a workaround.
4. Refresh the execution. In its **Tests** table, find the dummy Test and open
   its **Test Run** detail/execution view. Look for native iteration rows, not
   the comment text. Record whether exactly two rows persist with FAIL then
   PASS, and the Test Run's aggregate is FAIL. Refresh again to confirm storage.
   UI labels vary; if no native iteration view is available, record “not
   observable,” not success. Check the dummy Test's execution history too.
5. Reimport the same forward file into this same disposable execution. Check
   whether row count stays two, doubles, or rows are replaced. Then import the
   complete reverse file. Expect exactly two persisted rows PASS then FAIL and
   aggregate FAIL. These are desired observations, not guaranteed behavior.
6. Repeat the reverse import to check repeat behavior. Replacement, append,
   lost rows or failure-to-pass changes are findings. Never retry on a valuable
   run: complete imports may replace existing run details, comments or rows.
   For a clean order comparison, optionally create a second disposable execution
   and import reverse there first, reusing the same dummy Test.

Both payloads explicitly send overall FAIL. A FAIL readback therefore proves
that this summary survives import, **not** that Xray computes it from iterations.
Status/index alone cannot identify the original cases reliably after reordering.
Anonymous rows working is only partial capability; it does not establish named
parametrized support. Do not add undocumented `name`, parameters or datasets.

Exact question for Xray support (synthetic information only):

> For Xray Server/DC 8.5.3-j10, does a Generic/Unstructured Test (including a
> custom Automatic label mapped to that kind) accept status-only iterations
> through Xray JSON import? Which documented field provides stable case identity
> across reordered and repeated imports? The current iteration prose mentions
> name but the published closed schema does not establish that field. Are full
> reimports replacements or appends, and how is the Test Run summary determined
> when iteration statuses differ from the supplied overall status?

## Report back without sensitive information

- [ ] Offline demo: pass/fail; Python/pytest versions; sanitized error category.
- [ ] Optional sandbox: version/build and confirmed Generic kind (no URLs/keys).
- [ ] Forward/reverse: persisted native row counts/statuses and Test Run status.
- [ ] Repeat import: replaced/appended/unchanged/unknown; refreshed persistence.
- [ ] Stable identity: documented field confirmed by vendor, or still unknown.
- [ ] If rejected: sanitized error category, not raw response/logs/screenshots.

No workplace hostnames, issue keys, tokens, account names or test content should
be shared. “Not attempted” is a valid sandbox result.

Official background: [manual import action and JSON format](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301406948).
See [API uncertainties and readback plan](NATIVE-VALIDATION.md) for technical detail.
