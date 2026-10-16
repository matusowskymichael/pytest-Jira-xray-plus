# Architecture and product boundaries

The existing pytest11 entry point is `xray = pytest_xray.plugin`. This harness
adds no runtime module, network service, scheduler or alternative plugin entry.

| Area | Responsibility |
| --- | --- |
| `src/pytest_xray/plugin.py` | CLI options, configuration, choice of reporter/publisher. |
| `case_results.py` | Standard-library case/attempt/phase model and failure-preserving summary. |
| `case_report.py` | Captures pytest/xdist observations; controller writes local case JSON. |
| `xray_plugin.py` | Groups marked results by existing Jira Test key; creates aggregate import payload. |
| `comment_limits.py` | Bounds comment bytes after optional complete-payload archival. |
| `file_publisher.py` | Atomic JSON replacement for preview/archive files. |
| `xray_publisher.py` | Authentication and HTTP transport with timeout, redirect and response checks. |
| `tools/` | Existing synthetic reproductions, package build, installed-guide and docs checks. |
| `website/`, `mkdocs.yml` | Material site shell; tutorial/reference generated from README and docs. |
| `tools/agent.py` | Repository ledger/check orchestration, using fixed argv profiles and stdlib. |

The two report models intentionally differ. Local case summaries preserve any
observed failure; the inherited Xray grouping has ABORTED-over-FAIL priority.
Do not silently unify them. Generic is confirmed as the target Test type; the
exporter does not create, select or change that type. Parameter details are opt-in
comments, not native iteration rows. See [the guide](../../README.md).

Checks use localhost fakes and synthetic values. `validate_offline.py` blocks
requests and sockets; installed README checks block requests and scrub inherited
pytest/Xray configuration. None of this establishes live server compatibility.
The experimental JSON under `examples/native-probe/` is not plugin output.

The harness's preservation map is scoped to this tooling task, not a permanent
ban on future product changes. A later authorized task needs its own reviewed
scope and preservation map. Protected file changes fail visibly today.
