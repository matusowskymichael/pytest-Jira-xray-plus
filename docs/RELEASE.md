# Historical experimental alpha release: 0.1.0a1

For the current Jira/Xray integration workflow, use the [complete guide](../README.md).
The notes below record the original alpha scope, not current product positioning.

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

## Manual Trusted Publishing

The user has authorized the experimental alpha and configured a PyPI pending
Trusted Publisher for project `pytest-jira-xray-plus`, owner
`matusowskymichael`, repository `pytest-Jira-xray-plus`, workflow `publish.yml`,
and GitHub environment `pypi`. A pending publisher supports first publication;
no account-wide API token is necessary. It does not reserve the project name.

The workflow must be present on default branch `main` for manual dispatch.
It runs only through **Actions → Publish experimental alpha → Run workflow**,
never on pushes, pull requests or releases. Select `main`, enter its full
reviewed commit SHA, and leave `publish` unchecked for build validation only.
Check `publish` explicitly to upload version `0.1.0a1` after validation succeeds.
The expected SHA must exactly match the dispatched commit.

Global permissions are empty. The build/test job has only `contents: read`.
The publishing job has only `id-token: write`, uses environment `pypi`, and
performs no checkout or package installation. It downloads the exact artifact
ID from the successful build job in the same run, verifies the exact two file
names and SHA256 values, then uploads via PyPA's pinned publishing action with
metadata verification and attestations. Existing releases are not skipped.
Package/version/license metadata is checked before artifact upload; a clean
wheel smoke test must pass. Actions are pinned to commit SHAs.

GitHub environment protections are separate settings, not created by the YAML.
This public repository supports required reviewers and selected-branch rules,
including on GitHub Free. No reviewer or branch protection settings are changed
by this workflow. Its own job conditions restrict execution to this repository
and `main`. Additional protection settings require a separate decision; do not
assume a manual environment approval exists merely because `pypi` is named.

The pending publisher becomes ongoing publishing trust after first use. Future
versions require a reviewed workflow change because artifact names/version are
fixed at `0.1.0a1`. No password, API token or repository publishing secret is used.
Check PyPI and the successful workflow run to confirm publication; this document
is not evidence that an upload has happened.

Official requirements: [pending publisher for first upload](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
[manual workflow discovery](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow),
[environment protections](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).
