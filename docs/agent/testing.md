# Setup, verification and measured limits

Use Python 3.12+ in a fresh environment. Do not co-install upstream pytest-jira-xray.
Setup installs public development tools; it does not create credentials or call Jira:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e . -r requirements-tests.txt -r requirements-docs.txt build==1.6.1 setuptools==84.0.0 wheel==0.48.0 twine==7.0.0 'readme-renderer[md]' playwright==1.64.0
python -m playwright install chromium
```

For optional static diagnostics, use existing declared tools:

```sh
python -m pip install ruff==0.14.3 mypy==1.18.2 types-requests==2.33.0.20261006
```

PowerShell uses `.venv\Scripts\Activate.ps1`. Linux/macOS are the documented
shell examples; CI is Linux. Python 3.12, 3.13 and 3.14 are the existing matrix.
Set `CHROMIUM_PATH` to an installed Chromium when appropriate. The browser script
uses a temporary local server at the real Pages base path, not the hosted site.

Run a profile with `python tools/agent.py check --profile NAME`:

| Profile | Actual verification |
| --- | --- |
| `harness` | Nonempty stdlib unittest lifecycle/negative fixtures and architecture boundary checks. |
| `tests` | Existing `python -m pytest -q`, including the new harness tests. |
| `offline` | `tools/reproduce.py src --details` and `tools/validate_offline.py`. |
| `package` | Existing build, Twine checks, fresh owned venv, wheel install and all README examples/metadata. Requires package-index access for that venv's dependencies. |
| `docs` | Existing generator, strict MkDocs build, link check, desktop/mobile Chromium check. |
| `lint-baseline` | Existing Ruff rules across src/tests/tools; diagnostic, not a claimed green gate. |
| `type-baseline` | Existing mypy configuration across src/tests; diagnostic. |

Each profile uses fixed argv, fails on a nonzero/timeout/missing executable, and
writes JSON plus logs under `.harness/evidence`. It records the task, tested HEAD,
relevant content digest, exact normalized commands, status, exit codes and time.
Package checks recreate only the harness-owned `.harness/installed` environment.
Do not put work there. No command deletes tracked files, deploys or publishes.

## Baseline audit, 2026-10-16

At `8160bec9fb777fc86c28985040f8e4a46253dc6f` the working tree and remote main were
clean and equal; version is 0.1.3. Release CI recorded 115 tests and 14 installed
README commands on Python 3.12–3.14. That is historical evidence, not a new run.
There was no AGENTS.md, .agents skill, task ledger, tox/pre-commit config or shared
check entry point. Existing docs described API/report behavior but no module map.
`docs/VALIDATION.md` records an earlier 69-test validation and is now labeled historical.

Measured static baseline: mypy 1.18.2 reported no issues in 25 source files.
Ruff 0.14.3 reports five pre-existing issues: case_report.py line length, and
import order/line length in check_docs_browser.py and prepare_docs_site.py.
This harness does not rewrite runtime or hide those findings. Its own new files
must pass Ruff. Broad lint remediation is a separately scoped follow-up.

Dependency lower bounds and transitive dependencies are not a lockfile. Build
versions and docs tools are pinned, source archive metadata is normalized, and
CI/publisher hashes protect actual released files. Prior local and CI wheels
had different archive bytes despite identical member contents: do not promise
cross-host bitwise reproducibility. Record resolved versions with release evidence.

## October 26 action maintenance

PR #32 updates checkout to the immutable v7.0.1 SHA. Official
[checkout documentation](https://github.com/actions/checkout/blob/v7.0.1/README.md)
requires a Node 24 capable runner (2.327.1+); these workflows use GitHub-hosted
ubuntu-latest. Credential persistence remains disabled. The release workflow
checks out explicit main and never opts into unsafe fork checkout. Current
[release notes](https://github.com/actions/checkout/releases/tag/v7.0.1) document
the security/default-input fixes. No runtime usage commands change.

PR #33 updates setup-python to its immutable v7.0.0 SHA. Official
[release notes](https://github.com/actions/setup-python/releases/tag/v7.0.0)
describe the ESM migration and removal of the unused pip-install input. The
[README](https://github.com/actions/setup-python/blob/v7.0.0/README.md) retains
the Node24 runner requirement. Explicit Python versions (3.12–3.14) and current
installation commands remain unchanged; no token, permission or cache expansion.
