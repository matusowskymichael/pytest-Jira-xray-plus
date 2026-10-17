# In progress — reject blank upload base URLs

- Verified 0.1.8 release and operational evidence committed at a6f8dd82548de169c2043556f684c416b2757ce8. All three exact-head workflows passed (39007379442/39007379449/39007379448); clean remote/local main. Prior accepted ledger archived.
- Task XRAY-PRODUCT-008 on fix/blank-base-url. Installed 0.1.8 synthetic reproduction: empty/whitespace URLs run tests then exit 3 in all three auth modes, with transport blocked.
- Scope: helper blank-value guard only; preserve nonblank bytes, credentials/TLS, offline/collect-only and existing HTTP handling. Regressions and full-guide Unreleased notes added. Version/workflows/permissions unchanged.
- Next: focused tests/static checks, bind draft PR, run all five profiles and exact-head CI; fresh parent-arranged independent review before merge.
- No workplace/private data or browser security bypass. Live Generic 8.5.3-j10/custom Automatic mapping unverified; native iterations/datasets unsupported.
