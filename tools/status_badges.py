"""Generate first-party metadata snapshot badges; never deploy or write remotely."""

import ast
import datetime
import html
import json
import re
import urllib.request
from pathlib import Path

REPO = 'matusowskymichael/pytest-Jira-xray-plus'
PYPI = 'https://pypi.org/pypi/pytest-jira-xray-plus/json'


def write_badges(root, data, output):
    info = data['info']
    if info['name'] != 'pytest-jira-xray-plus' or not re.fullmatch(r'\d+\.\d+\.\d+', info['version']):
        raise ValueError('Expected this package and a published stable version')
    if not data['urls'] or any(item['yanked'] for item in data['urls']):
        raise ValueError('Expected non-yanked public distributions')
    if info['license_expression'] != 'Apache-2.0':
        raise ValueError('Unexpected published licence; review badge wording')
    workflow = (root / '.github/workflows/tests.yml').read_text()
    match = re.search(r'^\s+python: (\[[^\n]+\])$', workflow, re.M)
    if not match:
        raise ValueError('Python matrix not found')
    versions = ast.literal_eval(match[1])
    if not versions or any(not isinstance(v, str) or not re.fullmatch(r'3\.\d+', v) for v in versions):
        raise ValueError('Unexpected Python matrix')
    badges = {
        'pypi': ('PyPI snapshot', info['version']),
        'python': ('tested Python', ' | '.join(versions)),
        'license': ('licence', info['license_expression']),
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, (label, value) in badges.items():
        left, right = 8 * len(label) + 14, 8 * len(value) + 14
        title = html.escape(label + ': ' + value)
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{left + right}" height="20"
role="img" aria-label="{title}">
<title>{title}</title><rect width="{left}" height="20" fill="#555"/>
<rect x="{left}" width="{right}" height="20" fill="#007ec6"/>
<g fill="#fff" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">
<text x="{left / 2}" y="14">{html.escape(label)}</text>
<text x="{left + right / 2}" y="14">{html.escape(value)}</text></g></svg>'''
        (output / (name + '.svg')).write_text(svg)
    provenance = {
        'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'pypi_source': PYPI,
        'published_version': info['version'],
        'tested_python': versions,
        'license': info['license_expression'],
        'scope': 'Metadata snapshots; refresh after each release. Workflow badges separately show live main CI.',
    }
    (output / 'metadata.json').write_text(json.dumps(provenance, indent=2) + '\n')
    (output / 'index.html').write_text(
        """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Project status snapshots</title>
<h1>Project metadata snapshots</h1><p>These first-party badges record verified metadata, not live service queries.
Refresh after each release. Read the source and timestamp below; visit PyPI for the current release.</p>
<p><a href="https://pypi.org/project/pytest-jira-xray-plus/">PyPI releases</a> ·
<a href="metadata.json">Snapshot provenance</a></p>"""
        + ''.join(
            f'<p><img src="{name}.svg" alt="{html.escape(label + ": " + value)}"></p>'
            for name, (label, value) in badges.items()
        )
        + '<pre>'
        + html.escape(json.dumps(provenance, indent=2))
        + '</pre></html>'
    )
    return provenance


def main():
    root = Path(__file__).resolve().parents[1]
    with urllib.request.urlopen(PYPI, timeout=30) as response:
        data = json.load(response)
    print(json.dumps(write_badges(root, data, root / '.harness/status/public'), indent=2))


if __name__ == '__main__':
    main()
