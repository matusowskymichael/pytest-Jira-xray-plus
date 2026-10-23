# Maintaining this documentation site

The website uses Material for MkDocs, with original project colors and artwork.
Tutorial, how-to and reference pages are generated from the tested README.
The full PyPI README remains intact; do not edit generated `.docs-source` files.

## Build and preview

From the repository root in a development environment:

```sh
python -m pip install -r requirements-docs.txt
python tools/prepare_docs_site.py
python -m mkdocs build --strict
python tools/check_docs_links.py
python -m mkdocs serve
```

Open the localhost URL printed by MkDocs. No credentials are needed. The static
output is in `site/`; its links work under the repository's GitHub Pages path.
**Repository checker fix (0.1.10 source):** a page such as `class_index.html` keeps
its complete filename when resolving self-links. Only a file named exactly
`index.html` represents a directory URL. The 0.1.9 source checkout can report
false missing-file errors for coverage.py's `class_index.html` and
`function_index.html`, even when those files and their self-links are valid.
The fix allows checking a combined documentation/coverage site without removing
those links. Actual missing files or fragments still fail the command; external
URLs remain outside this local-file check. This does not change pytest reporting
or require a new plugin option.

The browser check in `tools/check_docs_browser.py` also exercises desktop/mobile
navigation, local search, clipboard copying and theme switching against a local server:

```sh
python -m pip install playwright==1.64.0
python -m playwright install chromium
python tools/check_docs_browser.py
```

Set `CHROMIUM_PATH` if using a system Chromium installation. Screenshots are saved
to `/tmp/xray-site-preview` by default; set `DOCS_SCREENSHOTS` to choose another path.
The existing package CI separately executes the README commands against an installed
wheel on Python 3.12, 3.13 and 3.14.

## Publishing model

CI only builds, validates and uploads a reviewable site artifact using repository
read permissions. It does not grant itself Pages deployment or identity-token
permissions. After review, publish the verified static files on `gh-pages` using
existing repository write access. Pages serves the root of that branch; `.nojekyll`
keeps the static files intact.

The public site is configured to deploy from `gh-pages`, at `/(root)`. Publication
uses the maintainer's existing repository access; no custom domain, extra token,
or new publishing credential is required. CI does not publish automatically.

## Deploy manually from main

Use a clean checkout with existing push access. Start with the reviewed source:

```sh
git switch main
git pull --ff-only origin main
python -m pip install -r requirements-docs.txt
python tools/prepare_docs_site.py
python -m mkdocs build --strict
python tools/check_docs_links.py
```

Run the browser check above and confirm the checks for this commit have passed.
Then fetch the published branch so its history is preserved, and push the built
site (`ghp_import` is installed with MkDocs):

```sh
git fetch origin gh-pages:gh-pages
python -m ghp_import -n -p -b gh-pages -m "Publish reviewed documentation from main" site
```

A non-fast-forward rejection means the local deployment branch is stale; fetch
and review the remote state before trying again. Do not force-push. GitHub's
built-in Pages build serves the static files, including `.nojekyll`. Check the
[Pages deployment runs](https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions)
and open the [live tutorial](https://matusowskymichael.github.io/pytest-Jira-xray-plus/tutorial/install/)
and search before considering publication complete.

For a new repository, pushing its first `gh-pages` branch may automatically enable
Pages. Treat that push as publication and obtain the repository owner's publication
authorization first. This repository's public Pages publication is authorized.

## Dependencies

Material and MkDocs versions are pinned in `requirements-docs.txt`. Material's
maintainers currently list May 5, 2027 as its end-of-life date; review their
[maintenance and migration guidance](https://squidfunk.github.io/mkdocs-material/getting-started/)
before then. Content stays in ordinary Markdown for a straightforward migration.
