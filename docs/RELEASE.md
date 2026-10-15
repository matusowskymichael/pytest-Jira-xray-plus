# Packaging and release proposal

Repository: https://github.com/matusowskymichael/pytest-Jira-xray-plus
Working distribution name: `pytest-jira-xray-plus`. No PyPI reservation or
release is implied. Version `0.1.0.dev0` is an unreleased development version.

The drop-in module `pytest_xray` and pytest entry point `xray` are retained.
Do not co-install with upstream `pytest-jira-xray`: both own the same module.
A future namespace migration would need an explicit compatibility plan.

Before a release:

1. Confirm distribution-name availability and maintainer metadata. Preserve
   Apache-2.0 notices and upstream attribution; upstream author metadata is
   retained as attribution, not an assertion of endorsement.
2. Review the offline schema and compatibility matrix. The local case report
   and labelled comment fallback can be released without claiming native
   Xray per-case support. Native iterations require separate validation.
3. Build wheel/sdist, run `twine check`, install in clean environments and
   exercise the supported Python/pytest matrix. Current runtime validation
   is Python 3.12; inherited classifiers are not new validation claims.
4. Obtain separate approval for TestPyPI/PyPI distribution. Configure narrowly
   scoped release authentication only then. No publishing secrets, deployment
   credentials, OIDC grants, or publishing workflow are configured here.

The included GitHub Actions workflow runs tests and package validation with
contents:read only. It cannot publish a package. HTTP integration tests use
only a localhost fake server and synthetic credentials.
