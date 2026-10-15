# Server/DC compatibility research

The initial research target is Xray **8.5.3-j10**, with Generic/Unstructured
Tests. This is not a verified native integration claim. Offline reports work
without Xray; native iteration import has not been implemented or exercised.
The existing legacy publisher remains inherited from upstream. For Server/DC
status spelling, omit `--cloud`. GitLab runners do not change the JSON contract.

## Custom Test Type names

Xray distinguishes a configurable Test Type name from its underlying kind:
Steps, Gherkin or Unstructured. Default names are Manual, Cucumber and Generic.
Additional names can map to these kinds. A name or definition field alone is
not proof of the configured mapping or of native parameter support.
[Official Test documentation](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301696435).

Smallest read-only check: an existing administrator opens **Jira Administration
-> Manage apps -> Xray -> Manage Test Types**, chooses the context applying to
the project, and reads the Type column for the relevant custom name. A project
context overrides global settings. No setting change, screenshot, API export,
credentials or access grant is required for this project.
[Manage Test Types](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301663656).

## Native iteration limitations

Current Server/DC JSON docs broadly describe iterations across Test types,
which supports status-only Generic iterations in principle. The Manual-only
restriction specifically concerns iteration parameters and dataset creation.
Do not infer that Generic Tests support Manual datasets. Iteration name appears
in prose but is absent from the closed embedded schema; stable pytest case
association remains unresolved. General documentation does not prove runtime
behavior for a particular custom type or release.
[JSON import reference](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/301406948).

The inherited publisher uses `/rest/raven/2.0/import/execution`; docs also show
1.0 routes. These route numbers are not Xray application versions. Confirm
endpoint/schema support and replacement behavior in a separately authorized
synthetic sandbox before introducing native iterations. Import a complete
result set, not one request per parameter case. See [the unexecuted native
validation plan](NATIVE-VALIDATION.md).

## Version-specific sources

- [8.5.3 release notes](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/1932558358):
  released September 15, 2026; describes an Integrity Checker fix for invalid
  Test Step Result attachments, not new Generic dataset support.
- [8.5.0 release notes](https://getxraydocs.atlassian.net/wiki/spaces/XRAY/pages/1813479425):
  describes preservation of Test Step attachment snapshots.
- [Marketplace version history](https://marketplace.atlassian.com/apps/1211769/xray-test-management-for-jira/version-history):
  public metadata lists 8.5.3-j10 builds 2008005033 (Data Center) and 2008005032
  (Server). Keep the suffix when assessing compatibility.

A separately pinned 8.5.3-j10 import schema was not located. Current official
Server/DC documentation is the research baseline; native readback validation
is still required. No live Jira system was contacted during development.
