# API decision record — 2026-10-15

Official sources reviewed:

- [Cloud JSON format](https://getxraydocs.atlassian.net/wiki/spaces/XRAYCLOUD/pages/44565311)
- [Cloud import REST v2](https://getxraydocs.atlassian.net/wiki/spaces/XRAYCLOUD/pages/44577176)
- [Server/DC JSON import](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301406948)
- [Server/DC import REST](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301667997)

Both variants document a test-level comment and aggregate status, and support
an iterations array. Dataset-producing iteration parameters are documented
for Manual tests, not arbitrary Generic tests. Do not translate pytest
callspec.params directly into API iteration parameters for a Generic test.
Server/DC's iteration prose lists name, but its embedded IterationResult
schema omits name and disallows additional properties. This discrepancy needs
version-specific resolution before native serialization. The Cloud page's
anonymous rendering was partial during this review; detailed iteration schema
validation remains a release gate, not an assumed cross-deployment contract.

Decision: provide a transport-independent offline case report plus an opt-in
comment fallback using the already supported comment field. No new Xray JSON fields, native iterations or remote
requests are introduced. The word `parameters` appears inside comment text,
not as a field in an API iteration object. The existing --cloud switch controls
status spelling. The initial compatibility research targets Server/DC 8.5.3-j10; omit --cloud. See
[Server compatibility](SERVER-COMPATIBILITY.md) for the unresolved
custom Test Type mapping and minimal read-only metadata.

The follow-up independent API review should verify Cloud name/log/duration
support and Server/DC iteration replacement behavior. Any future iteration
implementation must group a complete Test Run's results into one import;
per-case requests risk replacing earlier iteration data. Test type selection,
server version, custom status names, reruns and how comments/evidence map to
iterations are unresolved. Do not claim that this prototype populates the
Xray iteration UI or has been validated against a real instance.

## Upstream finding

Source: https://github.com/fundakol/pytest-jira-xray/tree/6ac1117585da590001cdbc2bf261b78683c19dcb

`XrayPlugin.pytest_runtest_logreport` merges results by Jira key.
`TestCase.merge` preserves failure over pass, appends comments and evidences,
and unions defects. Passing parametrized cases normally have empty comments,
so their identities and values disappear from the merged payload.
The offline baseline probe demonstrates this missing detail and explicitly
checks failure-then-pass remains FAIL. No Jira-side last-write behavior has
been reproduced. Issue [96](https://github.com/fundakol/pytest-jira-xray/issues/96)
provides relevant historical API discussion, not proof of current API semantics.
