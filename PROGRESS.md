# Review pending — reject blank upload base URLs

- Verified 0.1.8 release and operational evidence committed at a6f8dd82548de169c2043556f684c416b2757ce8. All three exact-head workflows passed (39007379442/39007379449/39007379448); clean remote/local main. Prior accepted ledger archived.
- Task XRAY-PRODUCT-008 on fix/blank-base-url. Installed 0.1.8 synthetic reproduction: empty/whitespace URLs run tests then exit 3 in all three auth modes, with transport blocked.
- Scope: helper blank-value guard only; preserve nonblank bytes, credentials/TLS, offline/collect-only and existing HTTP handling. Regressions and full-guide Unreleased notes added. Version/workflows/permissions unchanged.
- PR23: https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/23. All five profiles passed on f1f508ed2ca97b4d86e22d895a4926e607446ccd: 414 tests + 19 subtests, 32 harness tests, offline checks, build/Twine, all 14 installed README commands/full metadata, strict docs (23 pages/1210 references), local desktop/mobile/search/highlighting/theme. Changed-file Ruff and existing mypy (37 files) pass; all 13 profile log hashes verified.
- Content digest ba8a48ef301ecf621caa7ecd6a4157fc54d1d0597bf9fdc2cc43c6ffd3e2f48a. Runtime change is two lines; 31 new regressions preserve nonblank bytes and offline behavior.
- Next: exact frozen-head CI, then fresh parent-arranged independent review. Ledger stays review_pending; no merge or release before acceptance.
- No workplace/private data or browser security bypass. Live Generic 8.5.3-j10/custom Automatic mapping unverified; native iterations/datasets unsupported.
