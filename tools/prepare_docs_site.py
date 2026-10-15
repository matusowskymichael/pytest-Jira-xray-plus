"""Generate website pages from the tested README without changing the PyPI guide."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.docs-source'
readme = (ROOT / 'README.md').read_text()
sections = dict(re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', readme, re.M | re.S))
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / 'website', OUT, dirs_exist_ok=True)


def write(path, title, body):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f'# {title}\n\n{body.strip()}\n')


tutorial = [
    ('install', '1. Create a project'), ('cases', '2. Run two input cases'),
    ('xray', '3. Preview the Jira/Xray import'), ('upload', '4. Authenticate and publish to Jira/Xray'),
    ('local-report', '5. Audit cases behind a Jira Test Run'), ('values', '6. Choose audit report contents'),
    ('failure', '7. Diagnose a failing case'), ('archive', '8. Archive complete Xray comments'),
]
for index, (slug, heading) in enumerate(tutorial):
    context = ''
    if index:
        prev, prev_heading = tutorial[index - 1]
        context = f'<div class="step-context" markdown>\nContinue from [{prev_heading}]({prev}.md). '
        context += 'Use the same `xray-demo` folder and activated environment.\n</div>\n\n'
    write(f'tutorial/{slug}.md', heading, context + sections[heading].replace('Jira/Xray prerequisites above', '[Jira/Xray prerequisites](../reference/prerequisites.md)'))
write('tutorial/index.md', 'Integrate pytest with Jira and Xray', """
Begin with the [Jira/Xray prerequisites](../reference/prerequisites.md): your server,
Test and Test Execution issues, effective Test type and existing credentials.
Install the plugin, map your test, preview the payload, then authenticate and import
results. Debugging and audit recipes follow the core integration workflow.

""" + '\n'.join(f'- [{heading}]({slug}.md)' for slug, heading in tutorial) + """

Preview commands do not contact Jira. CI executes these commands against an installed
package with HTTP blocked; live imports require your authorized Jira/Xray environment.
The target Xray 8.5.3-j10 and custom Automatic mapping remain unverified.
""")
write('reference/prerequisites.md', 'Jira/Xray prerequisites', sections['Jira/Xray prerequisites'])
for path, heading in [
    ('reference/options.md', 'All package options'),
    ('reference/settings.md', 'Authentication and execution settings'),
    ('reference/compatibility.md', 'Result rules and compatibility'),
    ('reference/troubleshooting.md', 'Troubleshooting and migration'),
    ('guides/hooks.md', 'Advanced: customize the export with hooks'),
    ('project/development.md', 'Project and development'),
]:
    write(path, heading, sections[heading])
recipes = dict(re.findall(r'^### ([^\n]+)\n(.*?)(?=^### |\Z)', sections['Optional recipes'], re.M | re.S))
for path, heading in [('guides/parallel.md', 'Parallel tests and retries'),
                      ('guides/multiple-tests.md', 'Associate one function with multiple Tests')]:
    write(path, heading, 'Use the passing example from [the tutorial](../tutorial/xray.md).\n\n' + recipes[heading])
schema = (ROOT / 'docs/CASE-REPORT.md').read_text()
# Existing research documents use repository-relative links; keep them valid on the site.
schema = re.sub(r'\]\((?!https:|#)([^)]+)\)',
                r'](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/docs/\1)', schema)
write('reference/schema.md', 'Local JSON report schema', re.sub(r'^# .*\n', '', schema, count=1))
changelog = (ROOT / 'CHANGELOG.rst').read_text()
releases = re.findall(r'^(0\.1\.\S+ \(2026[^\n]*\))\n-+\n(.*?)(?=^0\.1\.|\Z)', changelog, re.M | re.S)
write('project/changelog.md', 'Changelog', '\n\n'.join(f'## {version}\n\n{body.strip()}'
      for version, body in reversed(releases)) + '''

## Earlier upstream history

See the [complete changelog](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/CHANGELOG.rst)
and [NOTICE](https://github.com/matusowskymichael/pytest-Jira-xray-plus/blob/main/NOTICE) for upstream attribution.
''')
print(f'Generated {len(list(OUT.rglob("*.md")))} documentation pages from the tested README and project sources')
