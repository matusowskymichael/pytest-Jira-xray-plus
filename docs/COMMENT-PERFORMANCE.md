# Comment aggregation: 0.1.13

The November 27 optimization buffers fragments only inside ordinary `TestCase`
aggregation. A single fragment remains a string without allocating a list. Public
reads materialize and cache the string; assignments discard pending fragments.
Subclasses and self-merge retain the legacy assignment order. Copy/serialization
materializes pending comments before exposing object state, preventing shallow
copies from sharing a mutable fragment buffer. Python documents the default
[object state protocol](https://docs.python.org/3.12/library/pickle.html#object.__getstate__);
this project supports Python 3.12 and newer. Cross-version pickle persistence is
not a package format contract.

No streaming JSON, marker-hook or case-report changes. Status priority, evidence,
defect deduplication, Generic Test grouping, result-hook dictionaries, truncation
and full archival content remain unchanged. xdist comments retain observed report
arrival order, which can vary across runs; no sorting is introduced. Hooks still
receive strings and can edit them before bounding/export. Reading after every
merge still materializes repeatedly; the optimization targets merge-many/read-once.

Run the repeatable isolated comparison with one interpreter:

```sh
python tools/benchmark_comments.py /path/to/baseline/src /path/to/candidate/src
```

It compares entire output dictionaries, includes serialization in timing, and
reports five samples plus medians for one, ten and 10,000 nonempty fragments and a
10,000-empty-fragment control. Each nonempty fragment contains 195 ASCII characters.
These are isolated TestCase measurements, not end-to-end pytest or Jira timings.
The parent's Windows CPython 3.14.5 experiment is separate evidence and must not
be pooled with this Linux CPython 3.12 environment. Current measured results and
installed CLI checks are recorded in the task's versioned evidence after testing.

`tests/test_comment_buffer.py` verifies separators, Unicode, empty comments, public
assignment, repeated serialization, self-merge, subclass descriptors, copying,
status/evidence/defects, exact full-archive bytes and deterministic deferred joining.
Its real serial/xdist CLI checks record arrival fragments before aggregation and
assert the exact final order. They do not normalize order or drop comments. All
HTTP requests are blocked; no workplace/live Jira compatibility is claimed.

Publication requires all existing release gates to pass. The
previous Forbidden artifact from publisher run 44710901682 must not be retried or
accessed through another route. Its missing comparison remains unverified.

## Linux CPython 3.12.14 isolated measurement

Five samples on the same executor/interpreter, including construction, merge and
final `as_dict`; complete dictionaries equal for every workload:

| Fragments | Baseline median | Candidate median |
| --- | ---: | ---: |
| 1 nonempty | 1.07 µs | 1.34 µs |
| 10 nonempty | 7.82 µs | 7.78 µs |
| 10,000 empty (control) | 4.84 ms | 6.18 ms |
| 10,000 nonempty | 616.93 ms | 7.76 ms |

The large nonempty case improved about 79× in this isolated measurement. The
single-fragment control has roughly 0.27 µs overhead. The empty control is about 1.34 ms slower for
10,000 fragments. Small timings vary with noise and allocator state.
Do not extrapolate these numbers to suite or network speed. Raw samples and exact
dictionary hashes are in `docs/agent/evidence/XRAY-PERF-001-isolated-benchmark-reviewed.json`.

## Bounded CI continuation and matched controls

The exact-base constructor and incoming-comment path avoid needless descriptor
calls; subclasses still follow their public descriptors. Seven warmed alternating
AB/BA pairs compare clean installed 0.1.12 and the candidate under the same Python
3.12.14 and dependency versions. No-capture paired median changes were +0.14% /
−1.53% for one case, +4.22% / +1.63% for 1,000 cases, and +2.12% / −0.50% for
10,000 cases (serial / two xdist workers). Entire payloads match after removing
only timestamps. Identical-package serial controls ranged from −11.58% to +21.91%
per pair for one case, and −14.63% to +12.99% for 1,000 cases. These measurements
do not establish a material end-to-end no-capture regression or a universal speedup.

The updated isolated 10,000-nonempty-fragment median was 639.75 ms versus 7.63 ms
(about 84×). Empty fragments took 4.91 ms versus 5.94 ms: a measured 1.03 ms
overhead across 10,000 merges from buffer/type bookkeeping, not a hidden win.
The single-fragment median was 1.05 µs versus 1.53 µs. Raw samples are retained
in `docs/agent/evidence/XRAY-COMMENT-001-fastpath-isolated.json`,
`XRAY-COMMENT-001-fastpath-interleaved.json` and `XRAY-COMMENT-001-aa.json`.

Reproduce the installed no-capture comparison with:

```sh
python tools/benchmark_comment_controls.py /path/to/baseline/python /path/to/candidate/python
```

This continuation authorizes a verified merge only. It does not authorize tags,
PyPI publication, publisher dispatch or Pages deployment. Version 0.1.13 remains
a prepared candidate until separately authorized publication completes.
