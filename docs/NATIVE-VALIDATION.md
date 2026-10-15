# Proposed two-case native import validation — Xray 8.5.3-j10

Status: **not executed**. The plugin does not emit this payload. This plan is
for a separately authorized, disposable synthetic sandbox only; no workplace
credentials, data, screenshots or access are requested.

## Preconditions

1. Sandbox Xray 8.5.3-j10 matches the deployment's build family. An administrator
   confirms the synthetic Test's Generic/Unstructured kind in the effective project context under
   Manage apps -> Xray -> Manage Test Types. Do not infer it from its label.
2. Confirm the sandbox's supported Xray JSON import route and matching schema.
   Upstream uses `/rest/raven/2.0/import/execution`; official Server documentation
   also has 1.0 routes. Do not try alternate routes against a workplace system.
3. Use an existing disposable Test Execution and existing Generic Test with
   synthetic-only definitions. The example keys below are placeholders, not
   targets. Ensure no valuable iteration/dataset data would be replaced.

## Candidate input, pending those checks

Two pytest cases map to one existing Test Run. A single import carries both
statuses; there is no one-request-per-case loop. No `testInfo`, iteration
parameters, dataset, name, steps, evidence or undocumented extension is used.

```json
{
  "testExecutionKey": "SYN-100",
  "tests": [{
    "testKey": "SYN-1",
    "status": "FAIL",
    "comment": "Synthetic probe: case-a FAIL, case-b PASS; array order is provisional, not a proven identity contract.",
    "iterations": [{"status": "FAIL"}, {"status": "PASS"}]
  }]
}
```

Current official Server/DC JSON documentation broadly permits iterations for
all Test types; iteration parameters/datasets are restricted to Manual tests.
This status-only candidate tests the general claim for the configured type. It
cannot by itself prove stable named per-parameter support.

## Required readback checks

- Record the HTTP result, but do not accept HTTP success alone as evidence.
- Read the target Test Run through the documented Test Run lookup
  `GET /rest/raven/1.0/api/testrun?testExecIssueKey=SYN-100&testIssueKey=SYN-1`
  (after confirming route availability). Verify the returned run belongs to
  the intended synthetic Test/Execution and its aggregate status is FAIL.
- In the sandbox Test Run UI and any documented 8.5.3-j10 iteration read endpoint,
  verify exactly two persisted native iterations: first FAIL, second PASS.
  Do not invent an iteration endpoint if the Test Run response omits details.
  Record aggregate status and iteration count/statuses locally; no full export
  or screenshot needs to leave the sandbox.
- Repeat on a fresh synthetic execution with reversed order. Both iterations
  must persist and the aggregate must still be FAIL, not the last outcome.
- Repeat the complete import into the same disposable run, then try the
  reversed complete set. Determine replacement versus append semantics and
  whether identities/order survive. The implementation must not duplicate rows
  or erase a failure due to request ordering.
- Check case association: status/index alone is insufficient if order changes.
  Resolve the documented `name` prose versus closed-schema discrepancy for
  8.5.3-j10 with the vendor before introducing a case identifier. No unsupported
  name/parameter payload should be guessed to make the experiment pass.

Acceptance requires persisted per-case identity/status, deterministic repeat
behavior, and failure-preserving summary. If only anonymous status rows work,
report partial API capability; do not advertise complete parametrized support.
Continue shipping the transport-independent local report and explicitly labelled
comment fallback until this contract is established.

## Official references

- [Server/DC JSON format](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301406948)
- [Import REST](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301667997)
- [Test Runs REST](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301669283)
- [8.5.3-j10 release notes](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/1932558358)

The 8.5.3-j10 notes do not establish a new iteration contract. Current Server/DC
API documentation is the research baseline, not proof this configured type has
passed a native integration test.
