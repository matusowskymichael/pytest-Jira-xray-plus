# Experimental alpha release: 0.1.0a1

Distribution: `pytest-jira-xray-plus`. Native Xray iterations remain unverified.
The alpha offers offline case/attempt JSON and an optional legacy comment
fallback. It is intended for synthetic evaluation, not production guarantees.
Use `pip install pytest-jira-xray-plus==0.1.0a1` only after publication is confirmed.

Python >=3.12, pytest >=9.1.1,<10, requests >=2.34.2,<3 are conservative initial
bounds based on the tested baseline. Python 3.12 / pytest 9.1.1 is the validated
combination; newer allowed versions are not a claim of a tested matrix. The
xdist 3.8.0 and rerunfailures 16.7 integrations are tested optional plugins.
Do not co-install upstream: both packages provide `pytest_xray` / `xray`.
Apache-2.0 LICENSE and NOTICE ship in both archives; original author metadata
is attribution, not endorsement. Issue reporting goes to this fork's GitHub.

Network behavior is opt-in via inherited `--jira-xray` (including when supplied
in pytest configuration). Adding `--xraypath` selects local legacy JSON instead.
`--xray-case-report` alone is local only. Value capture and identity redaction
are separate opt-ins; IDs can themselves contain data. No native probe is run
by installation, pytest defaults, the validation kit or the release build.

## Rebuild without uploading

Use a fresh Python 3.12 environment and this reviewed source revision:

```sh
python -m pip install build==1.6.1 setuptools==84.0.0 wheel==0.48.0 twine==7.0.0
python tools/build_release.py release-dist
python -m twine check release-dist/*
```

The script uses an isolated temporary source copy, a fixed SOURCE_DATE_EPOCH,
pinned backend, and normalizes sdist timestamp/ownership/gzip headers. It never
uploads. Compare SHA256 hashes from two independent builds with the same Python
and build tools; reproducibility across different toolchains is not promised.
The wheel is built from the sdist by `build`. Install the final wheel in a clean
environment and run synthetic reporting before publishing. Do not upload stale
`dist/` files or mix different versions. The source kit is in the sdist/repository;
the wheel contains the runtime plugin and license metadata.

## Publication gate and smallest setup step

The user has authorized an honestly described alpha publication. No authorized
PyPI upload mechanism is connected yet. As checked on 2026-10-15, the project's
PyPI JSON endpoint returned 404: no public listing, not a reservation or proof
that the name will be accepted. Recheck immediately before upload.

First confirm the intended PyPI account exists, has a verified email and 2FA.
The user must handle account setup and any legal agreements personally. Never
paste passwords, API tokens or recovery codes into chat or commit them.

For a first manual upload to a new project, a PyPI API token needs permission to
create that project; an account-wide token may be required because a project
scope cannot be selected before the project exists. That broad credential must
not be created or supplied to this agent without explicit setup approval and a
secure secret mechanism. The smallest alternative is a user-run local Twine
upload of the reviewed archives using their own approved credential, then revoke
any temporary account-wide token. Once a project exists, scope future upload
tokens to only `pytest-jira-xray-plus`; maintainer upload rights suffice.

Trusted Publishing with a pending publisher is another option but establishes
persistent repository/workflow trust and needs explicit approval. None is
configured. No secrets, OIDC grants, release workflow or permissions were changed.

A merge is **not technically required** for a manual upload of artifacts built
from the reviewed development-branch commit. Keep the draft PR until checks pass;
merging or tagging is a separate decision. The current CI has contents:read only
and cannot publish. No GitHub release or PyPI upload is performed by this plan.

Official requirements: [PyPI account and token help](https://pypi.org/help/),
[PyPA build/upload guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
