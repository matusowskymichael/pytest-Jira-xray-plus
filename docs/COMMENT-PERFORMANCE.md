# Comment aggregation candidate: 0.1.13

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

Version 0.1.13 remains a candidate until the existing release gates pass. The
previous Forbidden artifact from publisher run 44710901682 must not be retried or
accessed through another route. Its missing comparison remains unverified.

## Linux CPython 3.12.14 isolated measurement

Five samples on the same executor/interpreter, including construction, merge and
final `as_dict`; complete dictionaries equal for every workload:

| Fragments | Baseline median | Candidate median |
| --- | ---: | ---: |
| 1 nonempty | 1.10 µs | 1.37 µs |
| 10 nonempty | 8.42 µs | 7.57 µs |
| 10,000 empty (control) | 8.13 ms | 6.62 ms |
| 10,000 nonempty | 653.72 ms | 9.32 ms |

The large nonempty case improved about 70× in this isolated measurement. The
single-fragment control has roughly 0.27 µs overhead. Empty/small timings vary with
noise and allocator state; an earlier empty control was slower in the candidate.
Do not extrapolate these numbers to suite or network speed. Raw samples and exact
dictionary hashes are in `docs/agent/evidence/XRAY-PERF-001-isolated-benchmark.json`.
