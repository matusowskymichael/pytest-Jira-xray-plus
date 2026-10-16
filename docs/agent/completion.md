# Completion and evidence

A task is not passing because code was generated, a checkpoint exists or old CI
was green. Every required profile must have passed on the current relevant content,
and a fresh independent reviewer must cover every acceptance criterion with no
unresolved findings. Hosted CI and independent scope review remain PR requirements. Standing maintainer
authorization removes repeated user merge permission, not these acceptance gates.

Use `check --profile NAME --record-dir docs/agent/evidence` to prepare versioned
receipts and logs for acceptance. Default `.harness/evidence` is local working
feedback; it cannot serve as durable accepted proof. Inspect/redact logs before
sharing. The runner scrubs inherited Xray/pytest settings and known secret values;
this is not a guarantee against arbitrary sensitive output.

Receipts bind task ID, relevant content digest, tested HEAD, timestamp, the full
fixed argv list, each exit code, and log hashes. Missing, failed, incomplete,
changed or stale receipts are rejected. Evidence/progress/execution state are
excluded from the digest to avoid self-reference; scope, ownership, required checks,
preservation rules and common harness policy are included. A later commit containing
only evidence may use the same content proof; a changed requirement may not.

A reviewer creates a JSON file under `docs/agent/evidence` with:

- `task`, `digest` from preflight; `revision` is the current full HEAD.
- timezone-aware `timestamp` after the checks; `reviewer` distinct from `implementer`.
- `independent: true`, `verdict: "pass"`, `findings: []` only when actually justified.
- `acceptance`: every criterion string in the ledger, evaluated against real evidence.

The implementing agent must not author its own passing review. A human or separately
authorized fresh reviewer reads scope, diff, receipts and limits without relying
on the builder's conversation. Then the operator can run:

```sh
python tools/agent.py accept --task XRAY-PRODUCT-001 --evidence docs/agent/evidence/RECEIPT.json --review docs/agent/evidence/REVIEW.json
```

Supply all required profile receipts, not the illustrative single filename above.
The validator is a correctness aid for a trusted repository, not authentication or
a tamper-proof attestation system. It cannot prove that a reviewer is a distinct
person or that hand-edited files are truthful; review and hosted CI are essential.
The current task stays in progress/review pending until that real review happens.

No local check proves live Xray 8.5.3-j10 behavior. Generic is confirmed; native
iterations/datasets are still unsupported. No harness result changes release scope.

Package-profile digests include the complete fixed file/directory input set of
`build_release.py`, including MANIFEST.in, license/notice, both READMEs, changelog
and examples. Filesystem enumeration includes Git-ignored inputs copied by that
builder and applies the same cache exclusions. Evidence/progress remain excluded
intentionally; archived evidence bytes are not a claim of reproducible release bytes.
Missing historical evidence commits require fetching history, never accepting an
unresolvable revision. Reopened dependents must meet the same acceptance checks.
