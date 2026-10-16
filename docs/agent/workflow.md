# Session workflow and recovery

Start in the selected plugin checkout. Read AGENTS.md, PROGRESS.md, the ledger
and its linked scope; inspect branch/HEAD/status. Preserve unrelated edits.

```sh
python tools/agent.py preflight
python tools/agent.py resume
python tools/agent.py drift
```

Preflight validates schema, links, preservation and any passing evidence. It
reports dirty files rather than erasing them. It does not install dependencies,
run tests or contact remote services. Missing tools surface when their checks run.

After the draft PR is linked, use `python tools/agent.py drift --remote` to read
its current body with existing `gh` access. An unavailable source is not a pass.
A changed source blocks drift; review the change with the owner and update both
snapshot and ledger hash, then reverify. Local drift never claims remote freshness.
The initial source is the preserved user request; no GitHub issue was invented.

## Work on one bounded task

`start --task XRAY-ID-001` checks eligibility and passing prerequisites. Existing
active/review-pending/regression work prevents another activation. Implement only
the selected scope, run the applicable profiles, and inspect their result files.
Do not run publishing workflows as a verification shortcut.

```sh
python tools/agent.py check --profile harness
python tools/agent.py check --profile tests
python tools/agent.py check --profile offline
python tools/agent.py check --profile package
python tools/agent.py check --profile docs
```

A failed command produces failed evidence and leaves task state unchanged. Diagnose
its actual output; fix scope-relevant defects, then rerun that profile. Missing
dependencies mean environment setup is needed, not that the feature is broken.
Use `block --task ID --summary 'reason and next command'` for an actionable blocker.
Do not lower a required gate, rewrite a failing result or remove tests to pass.

## Checkpoint/resume

Update PROGRESS.md with verified/failed/not-run checks, current scope, limitations
and next executable action. Then create a local checkpoint:

```sh
python tools/agent.py checkpoint --summary 'Measured progress and outstanding review' --next 'python tools/agent.py resume'
python tools/agent.py resume
```

Checkpoints live in ignored `.harness/` and include checkout path and content digest.
A new clone uses versioned progress; it must create its own checkpoint. Changed
content or a different checkout makes the old checkpoint fail visibly. Inspect
changes, preserve useful work, reverify as needed and checkpoint again. Never
recreate an old absolute directory or reset Git to satisfy a checkpoint.

Passing evidence becomes stale when relevant source, scope or check definitions
change. `reopen --task ID --summary 'reason'` atomically invalidates the selected
task, all other stale passing proofs, and their transitive dependents. Affected
tasks become blocked; the selected task becomes regression only if its prerequisites
pass and no unrelated task is active. Reopening a dependent first is safe: reopen
and repair its prerequisite next. Old receipts remain historical references and
cannot satisfy acceptance after relevant content changes. Full validation precedes
the single ledger write, so failure cannot persist partial recovery. No automatic
rollback or unattended repair.

Commit reviewed source and handoff records and cite actual hosted CI for that head.
Prepare each candidate PR for independent review first. During the standing
maintainer window, independently accepted iterations with green exact-head checks
may merge and release without another user merge-permission prompt. Preserve
receipt history with merge commits; follow the existing manual trusted publisher
and Pages workflows. Do not weaken gates or change access settings.

At a new authorized product iteration, archive the completed ledger under evidence
with its accepted commit provenance and replace the current ledger with the new
task. Historical evidence stays tied to its old digest/commit, not asserted passing
on new product content. Reopen handles regressions within the current task graph.

Accepted receipts/reviews may identify earlier commits. Harness CI fetches full
history (`fetch-depth: 0`). In a shallow local clone, missing evidence history
blocks validation with `git fetch --unshallow` as the next command. Fetch history
explicitly, then retry preflight; do not discard revision checks or rewrite proof.
