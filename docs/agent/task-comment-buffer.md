# Buffer aggregated Xray comments

The user separately approved the measured first optimization on November 27
(Sentinel_0034fd46036881918c61afee8c8e0aeb). Optimize only TestCase comment
aggregation by buffering fragments and joining on materialization. Preserve public
comment reads/assignments, separators, empty comments, observed arrival order,
status, defects, evidence, subclass behavior, repeated serialization, result hooks,
truncation and full archival bytes. Do not change streaming JSON, marker hooks,
case reports or PR42. Use synthetic data only, no workplace access or credentials.

Compare baseline and candidate under matched isolated merge workloads, including
small/control workloads; do not claim isolated timings are end-to-end. Exercise
actual installed pytest CLI serial and xdist. Normalize timestamps only; for
xdist separately verify exact fragments/order against observed arrival input.
Run all five repository profiles, installed guide and package checks. Update
changelog, full beginner guide and relevant documentation. Prepare patch 0.1.13
only if available. Preserve release/security controls; version literals only in
the existing publisher. Start a draft PR, obtain independent exact-head review,
accept through the harness and merge only with fresh passing CI. Verify main.

Use existing trusted publishing only if every deployable-artifact and post-release
verification gate is available. Do not retry or route around the prior Forbidden
artifact from run 44710901682. A blocked release gate means report the actual merge
and publication status, not a bypass or an unverifiable release. No permission,
credential, account or settings expansion. Preserve certificate restrictions.
Stop after this single explicitly approved optimization.
