# In progress — correct built-site self-link checking

- 0.1.9 shipped at 5169981a955fa72c865dbaff7be5167a27c6aef6. Public install/all fifteen commands, exact artifacts/tag, 102 live Pages files and clean-source coverage verified. Release evidence at docs/agent/evidence/XRAY-RELEASE-005-release-0.1.9.json. Operational evidence commit 1581195362968ad38ce94720fdc5e725a90eae47 now has all three CI workflows green (39121931717/39121931666/39121931676); no failures required fixes.
- XRAY-DOCS-001 addresses false missing-file alarms for class_index.html/function_index.html self-links when checking a site with coverage output. One tool condition; no plugin/runtime/version/dependency/workflow changes or release.
- Next: baseline regressions, narrow fix, appropriate usage/changelog notes, full verification and draft PR for independent review.
- Environment healthy. No workplace/private data, new credentials/permissions or browser bypass. Live browser certificate limits and unverified Generic/custom Automatic mapping remain; native iterations/datasets unsupported. Deadline October 18 19:59 UTC.
