# Keep documentation validation active under optimized Python

The built-site checker uses assertions for missing targets/fragments and the
required search index. Running it with `python -O` or `-OO` removes those guards:
a synthetic page linking to missing.html exits zero and prints PASS. Replace
those two assertions with explicit failing exits, preserving link resolution,
validation boundaries and successful output. Test missing files, fragments and
search index plus valid-site controls in normal and both optimized modes.

This is one November 6 weekly maintenance iteration. Update the full beginner
guide's developer section, site maintenance docs and changelog. Reconcile completed
PR38 records, archive its accepted ledger at e06cb5e, and require fresh evidence.
No package/runtime/dependency/workflow changes or PyPI release are warranted.
No integration feature, GitHub approval action, credentials, account/permission
changes, workplace data/access or security-warning bypass. Preserve Generic Tests
on Xray 8.5.3-j10 and all privacy defaults; no live-server/native-iteration claim.

Authorized completion: draft PR, all five harness profiles, installed guide,
independent technical review, exact-head CI, accepted merge and main CI, then
existing Pages publication with normally validated HTTPS checks. Stop after this
iteration. Prior iterations and their permissions are historical, not active work.
