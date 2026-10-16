# Automatically tag successfully published versions on GitHub

User request, relayed by parent thread 01a12a8b-3ef6-705b-9250-4b8889b0701e:
"How can we do tagged released on GitHub? Can you set that up? So each time a new
version is done it’ll also be tagged on GitHub."

Complete 0.1.5 publication first, then prepare this separate harness/workflow PR.
Use current official API documentation and existing credentials. Automatically
create vX.Y.Z and a matching GitHub Release with version changelog notes and exact
successfully published PyPI artifacts, bound to the exact publisher commit.
Handle retries, failed publication, partial drafts and conflicts safely. Never
move/overwrite an existing tag, create credentials or republish used versions.

The proposed new job needs actions: read and contents: write on GITHUB_TOKEN.
Document and obtain explicit confirmation before enabling this additional scope;
preparing an inactive PR is authorized. Independent review is required before
merge. Keep the existing trusted publisher, package version and runtime unchanged.
Add synthetic regression tests, beginner release instructions and an unreleased
changelog note. Fix documentation generation only as needed to display these notes.
Record verification and exact live limitations. No browser security bypass.


Additional user scope: add truthful shared README badges for this project's PyPI
version, tested Python versions, licence, actual tests/docs workflows and measured
code coverage. Use existing GitHub/Pages; no new account/token/access expansion.
Measure every plugin source file, including Python subprocesses; explain line vs
branch scope, exact commit and snapshot freshness. Verify image URLs and both
GitHub/PyPI renderer output. Published 0.1.5 metadata cannot be replaced; show the
badges on live PyPI only via a later reviewed unused version. Keep one PR/iteration,
renew evidence and independent review, and do not claim unperformed live checks.
