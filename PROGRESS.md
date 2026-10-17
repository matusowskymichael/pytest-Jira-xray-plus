# In progress — authentication configuration errors

- PR19 independently accepted, merged at 3f144256ca910e37a64fb0542c16d6d7faa685f7 with identical accepted tree. Acceptance-head six workflows and main CI 39003343509/39003343499/39003343482 passed. Accepted ledger/review retained and archived.
- Task XRAY-PRODUCT-006: no open issues returned; code investigation reproduced missing auth configuration as INTERNALERROR/exit 3. Draft matrix on unchanged code: 22 expected failures, three offline/collection cases pass. Baseline excerpt/hash retained.
- Focused plugin configuration boundary converts existing auth helper XrayError to pytest.UsageError; no helper/HTTP/selection/TLS/version/workflow changes.
- Next: regression/documentation updates, five profiles, exact-head CI and fresh independent review. No release for version count.
- Published version remains 0.1.7. No workplace/private data or security bypass; live Generic 8.5.3-j10/custom Automatic mapping unverified, native iterations unsupported. One task at a time through 2026-10-18 23:59 Asia/Dubai.
