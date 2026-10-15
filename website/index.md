<div class="hero" markdown>

<div class="eyebrow">pytest Xray Plus · 0.1.1</div>

# Every pytest case, clearly reported.

Keep each input case and retry in a local JSON report. When you are ready,
export an aggregate result and readable case details to Jira Xray.

[Start the tutorial](tutorial/install.md){ .md-button .md-button--primary }
[See all options](reference/options.md){ .md-button }

Python 3.12+ · pytest 9.1.1–9.x · Open source · Apache-2.0

</div>

## Start locally. Add Jira when you need it.

```sh
python -m pip install pytest-jira-xray-plus==0.1.1
python -m pytest --xray-case-report=cases.json
```

Use a fresh environment: this fork cannot be installed alongside `pytest-jira-xray`.
The local report does not need Jira markers, credentials or a server connection.

<div class="grid cards" markdown>

- **Learn with one file**

    Build from two passing input cases to a local report, an intentional failure,
    and a reviewed Xray export. Copy complete examples and check the expected output.

    [Follow the tutorial →](tutorial/index.md)

- **Find the right command**

    Look up options, authentication settings and the exact rules for retries,
    skips and combined Jira results.

    [Open the reference →](reference/options.md)

- **Understand your reports**

    Keep structured cases in `cases.json`, a bounded Xray payload in `xray.json`,
    and complete comment text in an optional archive.

    [Compare report formats →](tutorial/xray.md)

</div>

## What reaches Xray?

One aggregate Test Run per Jira Test key, with optional case details in its comment.
**Native Xray iteration rows and datasets are not supported.** The local report
preserves the individual pytest cases independently.

[Read the compatibility boundaries](reference/compatibility.md) before applying
the exporter to a new server configuration.

## Keep this guide close

The [full tutorial is also on PyPI](https://pypi.org/project/pytest-jira-xray-plus/0.1.1/)
and in the [repository README](https://github.com/matusowskymichael/pytest-Jira-xray-plus#readme).
Website tutorial and reference pages are generated from that tested source so the
commands stay aligned across all three places.
