# In progress — report path configuration errors

- PR20 independently accepted and merged at 0d3c5f0086771eccb898f8b509839c4f725778a3; tree identical to acceptance commit b6116b8. Six acceptance-head workflows and main CI 39004455946/39004455979/39004455999 passed. Accepted ledger archived.
- XRAY-PRODUCT-007: no open issues returned. Synthetic unresolved home paths, Python 3.12 symlink loops and injected resolution failures reproduce internal configuration errors. Initial 28-case matrix: 21 expected failures, seven passes; two additional preservation cases pass before edits.
- Focused plugin normalization boundary maps only OSError/RuntimeError to option-specific UsageError. Non-strict resolution and writer boundaries unchanged; Python 3.13+ symlink loops may still fail later during writing.
- Next: regressions/docs, all five profiles, exact-head CI and independent review. No version bump or publication.
- No workplace/private data, new credentials/permissions or browser bypass. Live Xray/custom Automatic mapping unverified, native iterations unsupported. Continue one iteration at a time through 2026-10-18 23:59 Asia/Dubai.
