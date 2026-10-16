# Active iteration — collection lookup

- Task XRAY-PERF-001; branch perf/collection-key-lookup; baseline a18e361.
- Main, ledger, instructions, open PRs/issues and public PyPI reconciled: 0.1.6
  complete, no open work. No additional checkout skills found.
- Confirmed list membership in duplicate-key collection validation is quadratic.
- Scope: [task](docs/agent/task-collection-lookup.md). Preserve existing semantics;
  deterministic comparison benchmark, full profiles and independent review required.
- No version bump or publication. No workplace access/private data/security bypass.
- Next: reproduce comparison growth and add behavior regressions before patching.
