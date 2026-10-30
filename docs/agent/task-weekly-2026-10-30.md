# October 30 weekly maintenance: build backend setup

Fix the reproduced stale README backend pin (84.0.0 versus the manifest's
84.2.0) and repeated CI/publisher pin drift by reading build-system.requires
from the checkout. Keep the non-isolated builder and all validation gates.
Update the full beginner guide, changelog and maintainer setup instructions.
Do not merge separate bot PRs #36–38 in this iteration. No package release:
this change is repository tooling and documentation only.

User's current scheduled task: "Existing authorization covers scoped tested and independently reviewed commits/PRs, merging accepted maintenance, GitHub Pages updates and stable PyPI releases through existing trusted publishing." "Jira plus Xray are hard requirements, targeting Generic Tests on on-premises Xray 8.5.3-j10; do not claim workplace validation or native iterations without evidence." "No workplace access, real Jira data or credentials, purchases, new accounts, credential/permission expansion, destructive cleanup or security-warning bypass."

One iteration, then stop. Independent technical review is required; no GitHub PR
approval action without specific action-time user confirmation. Start a draft PR.
The existing release remains 0.1.10. Preserve runtime, dependencies, permissions,
artifact checks, publishing opt-in and compatibility/privacy defaults.
