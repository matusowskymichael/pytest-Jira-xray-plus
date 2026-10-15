<div class="hero" markdown>

<div class="eyebrow">pytest Xray Plus · Jira/Xray integration</div>

# Publish pytest results to Jira and Xray.

Map pytest tests to Jira Test issues. Run your parametrized suite and import
aggregate results into an Xray Test Execution, with case details in comments
when you enable them.

[Start the integration guide](reference/prerequisites.md){ .md-button .md-button--primary }
[Configure authentication](reference/settings.md){ .md-button }

Jira with Xray required · Python 3.12+ · pytest 9.1.1–9.x

</div>

## Connect your tests to your Jira workflow

You need Jira with the Xray app, existing Test and Test Execution issues, and
credentials with permission to import results. The requested target is on-premises
**Xray 8.5.3-j10**. Its exact configuration and custom **Automatic** Test-type mapping
still require live validation; this guide does not claim verified native iterations.

The guide takes you through installation, a marked parametrized test, an Xray
payload preview, authentication and import. You then inspect the Test Run in Jira.

<div class="grid cards" markdown>

- **Map and publish results**

    Associate cases with an existing Jira Test and target an existing Test Execution.
    Preview the payload, then send it using protected environment variables.

    [Follow the integration tutorial →](tutorial/index.md)

- **Configure your integration**

    Find Server/Data Center authentication, execution settings, status rules and
    exact compatibility limits before applying the exporter to your project.

    [Open the reference →](reference/settings.md)

- **Debug and audit an import**

    Inspect Xray JSON before sending, retain structured pytest cases and archive
    full comments. These facilities support the Jira/Xray integration.

    [Inspect the import preview →](tutorial/xray.md)

</div>

## What reaches Jira/Xray?

One aggregate Test Run per Jira Test key, with opt-in case details in its comment.
**Native Xray iteration rows and datasets are not supported.** The local audit
report preserves individual pytest cases, but it is not an Xray import format.

Offline previews deliberately make no network request. They help review data;
they do not establish valid credentials, permissions, issue keys or server mapping.

[Read the compatibility boundaries](reference/compatibility.md).

## Complete documentation

The full guide is preserved in the
[repository README](https://github.com/matusowskymichael/pytest-Jira-xray-plus#readme)
and packaged for [PyPI](https://pypi.org/project/pytest-jira-xray-plus/).
Website tutorial and reference pages use that same source.
