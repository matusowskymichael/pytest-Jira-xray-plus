# Harness adoption and limits

Primary source: [WalkingLabs English course](https://walkinglabs.github.io/learn-harness-engineering/en/).
The course is a design reference; the owner's scope in [task.md](task.md) is authority.
This implementation uses the existing Python toolchain and standard library.
It adds no model runtime, autonomous loop, service, database, or production dependency.

## Applicability and evidence

The numbered rows map the course's 14 lecture topics to this repository. Verification
is executable in `tests/agent/test_harness.py` and the profiles in `tools/agent.py`.
Structural adoption does not establish improved model performance.

| Topic | Disposition and mechanism | Evidence / limitation |
| --- | --- | --- |
| 01 Reliability beyond model capability | Adopt explicit acceptance and verification | Passing requires checks and independent review; no model benchmark claimed |
| 02 Instructions, tools, environment, state, feedback | Adapt to Python CLI and existing tools | Preflight, profiles, receipts and progress |
| 03 Repository as operational record | Adopt versioned scope and ledger | Source hash and optional GitHub body comparison; user instructions retain authority |
| 04 Short instruction map | Adopt AGENTS.md with progressive links | Local documentation link checks |
| 05 Cross-session state | Adopt versioned progress and local checkpoint | Checkpoint/resume and stale-checkpoint fixtures |
| 06 Separate initialization | Adapt to documented venv setup | Preflight never installs dependencies or credentials |
| 07 Bounded scope | Adopt one active task and preservation map | Concurrent-task and protected-runtime fixtures |
| 08 Feature lists | Adapt validated task ledger | Missing prerequisites, cycles, unknown checks rejected; passing can explicitly reopen |
| 09 Evidence-based completion | Adopt content-bound receipts and review | Missing/failed/stale/tampered evidence and self-review rejected |
| 10 Full verification pipeline | Reuse tests, offline, installed package and docs checks | Existing CI remains intact; new harness CI supplements it |
| 11 Observability | Adopt concise progress and redacted command logs | Secret-environment removal and output-redaction fixture; no private reasoning logs |
| 12 Clean handoff | Adapt checkpoints and pending review | Preserve user work; no automatic reset, merge or publication |
| 13 Controlled loops | Adopt explicit check/fix/recheck lifecycle | Interrupted, timed-out and unavailable commands leave non-passing receipts |
| 14 Dependencies | Adopt small validated dependency graph | Cycles, missing prerequisites and concurrent work rejected; no graph service |

## Other course material and reference implementation

The [course repository](https://github.com/walkinglabs/learn-harness-engineering)
contains projects, templates, resources, frontier harness descriptions and the
[harness-creator skill](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator).
The skill's instruction, state, verification, scope and lifecycle separation informs
this implementation. Its Node scaffolder is unnecessary in this Python repository;
we did not execute it or install its dependencies. Its distinction between structural
checks and actual agent evaluation is retained: real model performance evaluation
is deferred and has no passing score here.

The starter template's AGENTS/init/progress/feature-list pattern is adapted to
AGENTS.md, documented venv setup, PROGRESS.md, feature_list.json and the Python CLI.
The course project exercises are learning examples, not package release gates.
Frontier-agent architecture descriptions are background; custom runtimes, daemons,
multi-agent scheduling, persistent graph engines and telemetry services are deferred
because this focused plugin task needs none of them. A future adoption requires a
concrete owner-approved problem and measurable acceptance criteria.

Verified reference: [Ego City issue 2](https://github.com/matusowskymichael/ego-city/issues/2)
and [independent acceptance issue 4](https://github.com/matusowskymichael/ego-city/issues/4),
plus that repository's AGENTS.md and workflow/completion/testing/adoption documents.
Adapted ideas: executable recovery, per-task content digests, negative fixtures,
separate review and native toolchains. Game/browser gameplay gates were not copied.
No files in Ego City were changed. The prior private chat and FPLLab were not used
as verified sources.

Reading coverage: the English lecture structure, selected substantive lecture text,
template guidance, harness-creator instructions and the reference implementation
were inspected. This is not a claim to have read every project/resource/frontier
page, completed every exercise, or measured agents against course benchmarks.

## Deliberate departures

- Passing is reversible: changed relevant content requires an explicit reopen and
  fresh checks. The ledger cannot make old results true after source changes.
- GitHub is the review surface for task scope; local execution evidence is distinct.
  `drift --remote` fails when scope is unavailable or changed, rather than guessing.
- Evidence and handoff files are excluded from content digests to avoid recursive
  invalidation. Task criteria, check definitions, code and instructions are included.
- Independent review must come from a real separate reviewer. Fixture identities
  exercise validation only. This branch remains pending until review exists.
- Local checks cannot prove workplace Xray compatibility, native iterations, or
  real-world performance. Those limitations remain in the product documentation.
