"""Verify README examples against a specified installed interpreter, outside the checkout."""

import email.parser
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
readme = (root / 'README.md').read_text()
source = re.search(r'```python\n(.*?)```', readme, re.S).group(1)
python = str(Path(sys.argv[1]).absolute())
env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTEST', 'XRAY_', 'PYTHONPATH'))}
# Use the clean environment's installed pytest entry point, as the README does.
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory)
    sample = path / 'test_example.py'
    # Every run forbids HTTP, even if an environment or option unexpectedly enables it.
    (path / 'conftest.py').write_text("""import requests

def blocked(*args, **kwargs):
    raise AssertionError("README offline examples must never make HTTP requests")
requests.sessions.Session.request = blocked
""")
    for failing in (False, True):
        sample.write_text(source.replace('(2, 3)', '(2, 99)') if failing else source)
        for fallback in (False, True):
            args = [
                python,
                '-m',
                'pytest',
                '-q',
                'test_example.py',
                '--xray-case-report=cases.json',
            ]
            if fallback:
                args += ['--jira-xray', '--xraypath=xray.json', '--allow-duplicate-ids', '--xray-parameter-details']
            run = subprocess.run(args, cwd=path, env=env, capture_output=True, text=True)
            assert run.returncode == int(failing), run.stdout + run.stderr
            data = json.loads((path / 'cases.json').read_text())
            assert len(data['cases']) == 2
            assert sorted(c['status'] for c in data['cases']) == (
                ['failed', 'passed'] if failing else ['passed', 'passed']
            )
            subprocess.run([python, '-m', 'json.tool', 'cases.json'], cwd=path, check=True, stdout=subprocess.DEVNULL)
            if fallback:
                tests = json.loads((path / 'xray.json').read_text())['tests']
                assert len(tests) == 1
                assert tests[0]['status'] == ('FAIL' if failing else 'PASS')
                assert all(name in tests[0]['comment'] for name in ('one-plus-one', 'two-plus-one'))
                assert 'iterations' not in tests[0]
    print('PASS: installed README examples, passing/failing cases, both formats, no HTTP')

if len(sys.argv) > 2:
    wheel = Path(sys.argv[2])
    with zipfile.ZipFile(wheel) as archive:
        metadata_path = next(n for n in archive.namelist() if n.endswith('.dist-info/METADATA'))
        metadata = email.parser.BytesParser().parsebytes(archive.read(metadata_path))
        assert metadata['Description-Content-Type'] == 'text/markdown'
        assert metadata.get_payload().strip() == readme.strip()
    from readme_renderer.markdown import render

    html = render(readme)
    assert html and '<table>' in html and 'test_add_one' in html
    assert 'Troubleshooting and migration' in html and 'All package options' in html
    (wheel.parent / 'README-preview.html').write_text(html)
    print('PASS: complete README in wheel metadata; PyPI Markdown rendering checked')
