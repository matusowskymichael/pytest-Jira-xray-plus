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

Enabling Pages is a separate repository setting. It must be approved before it is
changed; prior PyPI Trusted Publisher authorization is not Pages authorization.
No custom domain, extra token, or new publishing credential is required.

## Dependencies

Material and MkDocs versions are pinned in `requirements-docs.txt`. Material's
maintainers currently list May 5, 2027 as its end-of-life date; review their
[maintenance and migration guidance](https://squidfunk.github.io/mkdocs-material/getting-started/)
before then. Content stays in ordinary Markdown for a straightforward migration.
