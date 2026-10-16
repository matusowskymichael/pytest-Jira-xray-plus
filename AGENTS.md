# pytest-Jira-xray-plus

Python pytest integration with **Jira plus Xray**, targeting existing **Generic
Tests** on on-premises Xray **8.5.3-j10**. Stable release: **0.1.3**. The plugin
imports aggregate Test Runs; native iterations/datasets are not implemented.

## Start here

Use Python 3.12+. From this repository root:

```sh
python tools/agent.py preflight
python tools/agent.py resume
python tools/agent.py check --profile harness
python tools/agent.py drift
```

These commands use the standard library. Other profiles require the development
environment in [testing](docs/agent/testing.md). `preflight` checks structure and
scope, **not** application correctness. Read [progress](PROGRESS.md) and the
[task ledger](feature_list.json) before selecting work.

## Read what the task needs

- [Architecture and boundaries](docs/agent/architecture.md): plugin/report/import flow.
- [Current scope](docs/agent/task.md): authorized harness change and acceptance criteria.
- [Workflow and recovery](docs/agent/workflow.md): start, verify, checkpoint, resume.
- [Testing](docs/agent/testing.md): exact commands, environments and baseline debt.
- [Completion](docs/agent/completion.md): current evidence and independent review.
- [Course adoption](docs/agent/harness-adoption.md): sources, adaptations and deferrals.
- [User guide](README.md), [API decision record](docs/API.md),
  [server limits](docs/SERVER-COMPATIBILITY.md), [release evidence](docs/RELEASE-READINESS.md).

## Invariants

- Preserve unrelated edits. Never reset, clean or restore user work to obtain a green tree.
- Keep one implementation task active; honor prerequisites and the selected scope.
- Treat user requirements as authority. Reconcile changed GitHub scope explicitly.
- Never use a workplace server, private data or real Jira credentials for routine checks.
  Tests use synthetic data, localhost mocks, or blocked transport. Preview export needs
  `--xraypath`; `--jira-xray` alone selects upload.
- Keep credentials and private payloads out of logs. Log concise decisions and results,
  not hidden reasoning transcripts. Inspect evidence before sharing.
- Preserve Generic targeting, documented aggregation/failure semantics and privacy opt-ins.
  A local pass does not prove live Xray compatibility or native iteration support.
- Do not weaken tests, scope, or evidence validation to mark a task passing. Changed
  relevant content invalidates old evidence; reopen work explicitly.
- Do not merge, release, deploy Pages, change credentials or expand permissions unless
  authorized for that action. Harness checks never perform those operations.
- End with current progress, exact verification limits and an executable next step.
  A checkpoint or draft PR is not independent acceptance.
