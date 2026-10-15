# Smallest user-run check for the target

No credentials, URLs, real issue keys, screenshots or workplace data need to be
sent to the maintainer. This task did not access a live server. Use only a separately
authorized disposable sandbox on the same Xray **8.5.3-j10** build. If none exists,
record “not attempted”; the version-specific compatibility claim stays blocked.

## What the official evidence does and does not establish

The current [Server/DC JSON format](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301406948)
allows iterations in its schema but documents parameter-bearing iterations for
Manual tests. Its iteration prose mentions name while its closed IterationResult
schema does not include that property. Therefore it does not establish named
pytest cases or datasets on a Generic test. The
[Server/DC import API](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301667997)
warns that reimport replaces existing dataset/iteration information.

Neither page is a pinned 8.5.3-j10 contract. Public searches did not locate an
authoritative version-specific contract resolving the Generic/name discrepancy.
A Jira platform API version, Cloud documentation, or an Automatic display label
is not evidence for this Xray app build. Ask the sandbox administrator/vendor to
confirm both the app build and Automatic's actual Generic/Unstructured type.
Do not change that type to make a test pass.

## A. Implemented comment fallback: one synthetic import

1. Use the README's two-case test, but change one expected result to 99. Run its
   offline fallback command, optionally adding the proposed `--xray-full-report`.
2. In the authorized sandbox, create one dummy Generic Test and one disposable
   Test Execution. Replace the dummy Test key in the local test and rerun; set the
   disposable execution key in the JSON's `testExecutionKey`. Keep keys locally.
3. Using your existing browser login, open that Test Execution and choose
   **Import Execution Results → Xray JSON**, selecting the bounded `xray.json`.
   No API token is required for this manual test. If the action is unavailable,
   stop rather than requesting credentials or trying another endpoint.
4. Refresh and open the Test Run. Verify aggregate FAIL and a comment containing
   both input identities, or the explicit truncation notice when deliberately
   testing a small bound. Check full text remains in your local archive.

This validates persisted comment behavior only, not native iteration support or
API authentication. Repeat with the intended comment limit before claiming that
limit works on the target; 32,000 bytes is a client policy, not a server guarantee.

## B. Native capability: three imports, only after schema/type confirmation

Use the same disposable Test and Test Execution, with no valuable data. Review
[forward.json](../examples/native-probe/forward.json) and
[reverse.json](../examples/native-probe/reverse.json); substitute the two sandbox
keys locally. These contain only synthetic statuses and explanatory text, and
are **not generated or uploaded by the plugin**.

1. Manually import forward: refresh and check whether exactly two native rows
   persist, FAIL then PASS, with overall FAIL.
2. Import reverse into the same execution: refresh and check whether exactly two
   rows persist, PASS then FAIL, with overall FAIL.
3. Reimport reverse: refresh and check whether the rows remain exactly two or
   duplicate. Record whether comment/rows were replaced.

These are desired observations, not promised outcomes. Overall FAIL was supplied
in the payload, so it does not prove server-side aggregation. Even successful
anonymous rows do not solve stable case identity. Named Generic support remains
blocked until the vendor confirms a field supported by this exact build and a
separate synthetic probe verifies it across reordered imports. Do not add `name`,
Manual-only parameters, or datasets based solely on the current prose.

Return only: build confirmed yes/no; Generic mapping confirmed yes/no; comment
persisted yes/no; native row counts/status order; repeated import replaced or
appended; supported identity field confirmed or unknown. No private content is
needed. A rejection or “not observable” is a useful result, not a reason to guess.
