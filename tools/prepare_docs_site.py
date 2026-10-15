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
    ('local-report', '3. Save that result locally'), ('values', '4. Choose what the local report contains'),
    ('failure', '5. See what happens when one case fails'), ('xray', '6. Prepare an Xray result without uploading'),
    ('archive', '7. Keep full comments when an export is shortened'), ('upload', '8. Send to Jira (optional)'),
]
for index, (slug, heading) in enumerate(tutorial):
    context = ''
    if index:
        prev, prev_heading = tutorial[index - 1]
        context = f'<div class="step-context" markdown>\nContinue from [{prev_heading}]({prev}.md). '
        context += 'Use the same `xray-demo` folder and activated environment.\n</div>\n\n'
    write(f'tutorial/{slug}.md', heading, context + sections[heading])
write('tutorial/index.md', 'A working report, one step at a time', '''
Start with two passing input cases and one Python file. Each page adds a concept,
explains its purpose and shows what you should see. Steps 1–7 run entirely locally;
uploading is an optional final step.

You need Python 3.12 or newer and a terminal. No Jira access is needed to begin.

''' + '\n'.join(f'- [{heading}]({slug}.md)' for slug, heading in tutorial) + '''

The command examples are executed against an installed package in CI, with network
transport blocked for local examples. The site uses the same source as the complete
PyPI tutorial. You can return to the reference pages at any time.
''')
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
