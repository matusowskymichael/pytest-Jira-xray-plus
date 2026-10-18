# Status badges and measured coverage

The shared README is the source for GitHub and the PyPI package description. It
shows only this project's version, tested Python versions, licence, tests,
documentation build and measured plugin coverage. No Discord, community service
or Codecov account is implied.

## What each badge means

| Badge | Source | Freshness |
| --- | --- | --- |
| PyPI snapshot | Public PyPI JSON for this package | Verified metadata snapshot; current PyPI release is linked |
| Tested Python | Existing test matrix: 3.12, 3.13, 3.14 | Metadata snapshot; install requirement remains Python 3.12+ |
| Licence | Published PyPI SPDX expression, Apache-2.0 | Metadata snapshot |
| Tests | Actual `tests.yml`, main push events | Live GitHub workflow status |
| Documentation build | Actual `docs.yml`, main push events | Live GitHub workflow status |
| Plugin lines | Coverage.py measurement of every `src/pytest_xray/**/*.py` file | Measured snapshot; report shows commit, timestamp and scope |

Metadata images and coverage are first-party files on the existing Pages site.
[Metadata provenance](https://matusowskymichael.github.io/pytest-Jira-xray-plus/status/)
and [coverage report](https://matusowskymichael.github.io/pytest-Jira-xray-plus/coverage/)
identify the snapshots. They can lag main or the current PyPI release; they do not
silently claim to be live. Refresh them after each release. GitHub/PyPI image
caches can delay a refresh. The external badge service returned HTTP 403 in the
builder environment; first-party images avoid relying on that service.

## Coverage scope

The badge is **line coverage**, computed as `covered_lines / num_statements`.
Branch coverage is recorded separately. Coverage.py's detailed report also shows
a combined line/branch Total; do not confuse that percentage with the badge.
The denominator is the plugin's 13 Python files, including unexecuted files.
Tests, repository tooling, dependencies and generated files are outside it.
Coverage.py's standard executable-line/exclusion rules apply; this project adds
no omission patterns or artificial percentage threshold.

The full pytest suite runs under coverage, with subprocess patching, separate data
files and combination after successful completion. This includes Python child
processes used by pytester and xdist. Coverage data is rejected if it omits a
plugin file or if totals disagree with per-file counts. All measurement uses
synthetic data, blocked transport or localhost mocks. A high percentage does not
prove live Jira/Xray 8.5.3-j10 compatibility, native iterations or correctness.

Initial published snapshot: clean 0.1.5 commit
`d007adeefe5057ed9dcbb6ce6c4d28ec7eff942e`, Python 3.12.14, coverage.py 7.16.2;
187 tests and 19 subtests passed. **714/745 executable lines (95.8%)** and
**211/240 branches (87.9%)** were covered. These are measured results, not a copied
badge percentage. The report records the measurement helper/configuration hashes.

## Reproduce and refresh

From the repository development environment:

```sh
python -m pip install -e . -r requirements-tests.txt
python tools/measure_coverage.py
python tools/status_badges.py
```

Coverage outputs are in `.harness/coverage/public/`: the SVG, raw measurement,
provenance and HTML report. `.harness/coverage/latest-tests.log` records the run.
Metadata outputs are in `.harness/status/public/`. The metadata command reads
public PyPI JSON with normal TLS; it neither publishes nor changes repository access.
To measure another clean checkout with the same installed test environment, use
`python tools/measure_coverage.py --root /path/to/checkout`. The helper explicitly
imports that checkout's plugin and reports its commit, dirty status and source hash.

CI measures coverage in the existing Python 3.12 test job and uploads
`plugin-coverage-python-3.12`; Python 3.13/3.14 still run their normal full suites.
The job retains read-only repository permissions. No coverage account, token,
third-party upload or automatic Pages write is added. A failed measurement cannot
upload a new success artifact or replace the published snapshot.

After checking a successful **main** run and its exact source commit, the authorized
maintainer copies that artifact's public files into `coverage/` on the existing
`gh-pages` branch and the metadata output into `status/`, then uses the existing
Pages deployment. When copying local output, remove the generated
`coverage/html/.gitignore` in the deployment copy so Git includes the HTML files.
Check the live hashes, image content types and provenance over
normal TLS. **When replacing the rest of the site, preserve `coverage/` and
`status/` unless explicitly refreshing them with verified outputs.** PR artifacts
are review previews, not an automatic replacement for the public main snapshot.
Artifact-storage failure must be reported; a separately executed clean-source
measurement can be published only with its actual local provenance identified.

## GitHub and PyPI rendering

All six README images use absolute HTTPS URLs and descriptive alt text. Native
GitHub status images link to the real workflow or documentation; metadata and
coverage snapshots link to the relevant public source/report. The package build
renders the complete README using PyPI's renderer and checks the installed tutorial.
GitHub Markdown rendering and live image responses are also checked during review.

An already-published PyPI distribution's README cannot be replaced. The **0.1.6** package README includes these badges. Publication requires review
and an unused version; the 0.1.5 page remains unchanged. Local PyPI-renderer checks
are preview evidence until the new public page is verified after publication.
Live browser checks remain blocked by the recorded certificate warning. Never
ignore TLS/security errors; use a trusted user browser for that final visual check.

Sources: [Coverage.py subprocess measurement](https://coverage.readthedocs.io/en/latest/subprocess.html)
and [GitHub workflow status badges](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge),
checked 2026-10-16.


## Checking a site that includes coverage pages

After copying the generated coverage report into `site/coverage`, run the existing
`python tools/check_docs_links.py` command against the combined site. The
unreleased repository checker fix preserves filenames such as `class_index.html`
and `function_index.html` when checking empty or fragment-only self-links. The
0.1.9 checkout can falsely report those links as missing because it treats any
filename ending in `index.html` as a directory index. Only the exact filename
`index.html` should use the directory URL. Genuine missing files/fragments and
the required search index remain failures. This is local static validation, not
a browser check or verification of remote links; do not remove valid coverage
links just to silence the old diagnostic.
