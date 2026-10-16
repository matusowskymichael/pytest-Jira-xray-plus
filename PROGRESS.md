# Completed iteration — 0.1.6 published and verified

- Task XRAY-RELEASE-002 is independently accepted; PR #14 merged.
- Published source: `b2c5b73bb771110129ede8b41cf5fb96447d81b3`; tree matches
  accepted commit `0b707306b134b87abcf8af25ecbc415f3bdccb29`. Six acceptance-head
  checks and all three main checks passed. No runtime/dependency/permission changes.
- [PyPI 0.1.6](https://pypi.org/project/pytest-jira-xray-plus/0.1.6/): trusted
  publish run 38912482897 after immediate unused-version/main-SHA verification.
- [GitHub v0.1.6](https://github.com/matusowskymichael/pytest-Jira-xray-plus/releases/tag/v0.1.6):
  automatic run 38912710605. Tag matches published commit; both downloaded assets
  hash-match PyPI and publisher outputs. Exact version notes attached.
- Fresh public installation: all 14 README commands and full README rendering pass.
  Public PyPI JSON description exactly matches shared README and contains six badges;
  image endpoints/links and GitHub renderer checked using normal TLS.
- Clean-source measurement: 253 tests + 19 subtests; 714/745 lines (95.8%) and
  211/240 branches (87.9%) across all 13 plugin files, including subprocesses.
  Provenance explicitly identifies actual local measurement on the release commit.
- Pages deployment 38912894000, branch commit `352e3cdf00fd714626a9aad540605a04889fcfb6`:
  all 101 live files hash-match deployment. Docs, coverage and 0.1.6 metadata refreshed.
- [Durable release proof](docs/agent/evidence/XRAY-RELEASE-002-release-0.1.6.json).
- Limits: PyPI project HTML returns Client Challenge here. Live browser certificate
  warning was not bypassed. Published metadata/normal-TLS checks and renderer previews
  pass, but live visual confirmation requires a trusted user browser. No workplace
  access/private data. Live Xray/custom Automatic mapping unverified; native iterations
  unsupported. Existing explicit permission approval remains valid.
- Next: `python tools/agent.py preflight`; confirm operational evidence commit CI,
  then hand off the live visual check. Do not reuse 0.1.6 or open another iteration
  without reconciling its authorized scope.
