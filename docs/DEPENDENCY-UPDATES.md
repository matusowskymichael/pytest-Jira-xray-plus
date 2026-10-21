# Dependency update maintenance

Dependabot version updates are configured in
[.github/dependabot.yml](../.github/dependabot.yml) for **Fridays at 09:00
Asia/Dubai (05:00 UTC)**. This is the configured check time, not a guaranteed PR
delivery time. GitHub can also start an initial check when the configuration is
added or changed. Checks target the repository's default branch, currently main.

## Coverage and review queue

| Ecosystem | Files / references | Open version-update PR limit |
| --- | --- | --- |
| `pip`, `/` | Root PEP 621 `pyproject.toml`, `requirements-tests.txt`, `requirements-docs.txt` | 5 |
| `github-actions`, `/` | Action references in `.github/workflows/*.yml`, including commit-pinned actions | 3 |

There is no Python lockfile. Python minor/patch version updates share one group;
Actions minor/patch version updates share another. Major updates remain eligible
as separate PRs: there is no ignore rule or major-version exclusion. Existing
version constraints and upstream resolver compatibility still apply; a package
already satisfying a broad range may not need a manifest edit. The limits count
open version-update PRs, not updates per week. Full queues can defer later PRs.

This does not maintain arbitrary `pip install` strings in workflow `run` blocks,
Python helper scripts, or documentation examples. Those include pinned build,
verification and installed-smoke dependencies and need manual reconciliation with
any proposed manifest update. The first Python bot log should also be inspected
for actual discovery of `[dependency-groups]` and `[build-system].requires` in
this project's pyproject; configuration alone is not proof that every declaration
was processed. No dependency version is changed by this setup.

## Maintainer workflow

1. Inspect each bot PR's changes and release notes, especially major updates.
   Reconcile repeated pins in manifests, workflows, helpers and documented commands.
2. Use the repository harness to open an appropriately scoped maintenance task.
   Dependency/workflow changes invalidate historical accepted proofs and may fail
   preservation checks until that task is explicitly reconciled. Keep those guards;
   do not bypass them to make a bot PR green. Rebase paused PR30 separately only
   when its own maintenance work resumes.
3. Run affected tests, all required task profiles, installed guide/metadata checks
   and exact-head CI; obtain independent review before merging. Future bot PRs are
   **not automatically merged**. A dependency PR does not authorize a release.
4. Check **Insights → Dependency graph → Dependabot** for update-job logs and
   discovery/resolution errors. Also inspect Dependabot workflow runs and opened
   PRs. A merged config proves installation, not successful execution; record the
   first actual result separately. If access/credentials or broader enablement
   are requested, stop and ask rather than expanding access.

These are version-update schedules. They do not establish security-alert coverage,
change security-update enablement, or constrain separately enabled security updates
to Friday. GitHub gives security-update PRs a separate internal limit; these two
limits govern version updates only. No new secrets, registry credentials, workflow
permissions, repository access, or auto-merge workflow is added.

Maintenance is weekly on Fridays; integration features require discussion before
implementation. Michael's October 21 request to set up Dependabot is a specific
exception to the pause. PR30 and other unrelated work remain paused.

## Sources and verification boundary

Checked October 21, 2026 against GitHub's official
[options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference),
[supported ecosystems](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories),
and [configuration setup](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates).
Local YAML/manifest validation and CI do not replace GitHub's first Dependabot job.
This configuration neither changes plugin reporting nor proves live Xray compatibility.
