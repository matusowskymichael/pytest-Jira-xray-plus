# Correct built-site self-links for index-suffixed filenames

After the 0.1.9 release and green operational-evidence main CI, fix the confirmed
repository documentation checker bug. The released site includes coverage.py
class_index.html and function_index.html; their valid empty self-links are
reported as missing files because removesuffix('index.html') changes the page
URL to class_ or function_. The ordinary MkDocs-only check passed, but adding
coverage exposed four false alarms. Independent exact-basename diagnostic
validated 41 HTML pages and 2911 references; no broken site file was found.

Change only tools/check_docs_links.py URL construction: canonicalize a directory
index only when its basename is exactly index.html. Preserve other filenames,
including filenames ending with that string. Preserve root/nested directory
indexes, relative paths/assets, query strings, decoded paths/fragments, existing
external/project-prefix boundaries, missing-file/anchor errors and search-index
requirement. No broad suppression, skipped empty links or network requests.

Add subprocess regressions with synthetic sites exercising root/nested indexes,
ordinary index-suffixed pages, empty/query/fragment self-links, relative files and
assets, encoded paths/fragments, genuine missing targets/anchors/search index and
external-link boundaries. Demonstrate failures before the fix and validate the
real site with released coverage/status included afterward. No plugin runtime,
existing tests, dependencies, publisher/workflows, version or harness changes.

Update Unreleased changelog, site-maintainer and coverage instructions plus a
brief beginner-friendly README maintainer note. Explain repository-only impact:
false build-check alarms removed; plugin install/export behavior unchanged. Keep
all fifteen executable guide commands. Archive the accepted release ledger and
record actual 0.1.9 publication evidence; retain privacy and Generic/on-prem
8.5.3-j10 limitations. All five profiles, installed guide/full metadata, changed
static checks and exact-head CI before a fresh parent-arranged independent review.
Prepare one draft PR; no quota release, deployment or publication in this task.

No workplace/private data, new credentials/accounts/permissions, purchases,
destructive cleanup or browser certificate bypass. Actual live-browser checks
remain blocked; normal-TLS public verification is separate. Native iterations
and datasets unsupported. Authorized maintenance ends October 18 19:59 UTC.
