"""Execute the actual README tutorial in order against an installed package."""

import email.parser
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
readme = (root / 'README.md').read_text()
python = str(Path(sys.argv[1]).absolute())
env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTEST', 'XRAY_', 'PYTHONPATH'))}
events = re.findall(r'<!-- (tutorial|run|json):(\w+) -->\s*```\w+\n(.*?)```', readme, re.S)
assert events, 'No tutorial steps found'
blocked = """import requests

def blocked(*args, **kwargs):
    raise AssertionError("README offline examples must never make HTTP requests")
requests.sessions.Session.request = blocked
"""


def subset(expected, actual):
    """Check a documented JSON excerpt, allowing explicitly omitted fields."""
    if isinstance(expected, dict):
        for key, value in expected.items():
            subset(value, actual[key])
    elif isinstance(expected, list):
        assert len(expected) == len(actual)
        for left, right in zip(expected, actual):
            subset(left, right)
    else:
        assert expected == actual


with tempfile.TemporaryDirectory() as directory:
    path = Path(directory)
    (path / 'conftest.py').write_text(blocked)
    seen = []
    for kind, name, content in events:
        if kind == 'tutorial':
            if name == 'hooks':
                (path / 'conftest.py').write_text(blocked + '\n' + content)
            else:
                (path / 'test_example.py').write_text(content)
            continue
        if kind == 'json':
            subset(json.loads(content), json.loads((path / 'cases.json').read_text()))
            continue
        args = shlex.split(content)
        assert args[0] == 'python' and args[1:3] == ['-m', 'pytest'] or args[:3] == ['python', '-m', 'json.tool']
        result = subprocess.run([python, *args[1:]], cwd=path, env=env, capture_output=True, text=True)
        assert result.returncode == (1 if name == 'failure' else 0), result.stdout + result.stderr
        seen.append(name)
        if name == 'basic':
            assert '2 passed' in result.stdout
            assert not (path / 'cases.json').exists()
        if '--xray-case-report=cases.json' in args:
            report = json.loads((path / 'cases.json').read_text())
            assert report['schema_version'] == 1
            assert report['pytest_exit_status'] == (1 if name == 'failure' else 0)
            assert len(report['cases']) == 2
            cases = report['cases']
            assert [c['status'] for c in cases] == (['passed', 'failed'] if name == 'failure' else ['passed', 'passed'])
            for case in cases:
                attempt = case['attempts'][0]
                assert attempt['complete'] is True
                assert [phase['phase'] for phase in attempt['phases']] == ['setup', 'call', 'teardown']
                assert ('parameter_values' in attempt) == (name == 'values')
            if name == 'values':
                assert cases[0]['attempts'][0]['parameter_values'] == {'value': 1, 'expected': 2}
            elif name == 'redact':
                assert {c['nodeid'] for c in cases} == {'case-1', 'case-2'}
                assert 'test_add_one' not in json.dumps(report)
            else:
                assert cases[0]['nodeid'].endswith('[one-plus-one]')
                assert cases[1]['nodeid'].endswith('[two-plus-one]')
        if '--xraypath=xray.json' in args:
            payload = json.loads((path / 'xray.json').read_text())
            assert len(payload['tests']) == 1
            test = payload['tests'][0]
            assert test['testKey'] == 'DEMO-1' and test['status'] == 'PASS'
            assert 'iterations' not in test
            if name == 'preupload':
                assert payload['testExecutionKey'] == 'DEMO-100'
            if name == 'xray':
                assert 'comment' not in test
            elif name == 'archive':
                assert 'truncated 1 comment(s)' in result.stdout
                full = json.loads((path / 'full-xray.json').read_text())['tests'][0]['comment']
                assert len(full.encode('utf-8')) > 256 >= len(test['comment'].encode('utf-8'))
                assert 'TRUNCATED' in test['comment']
                assert all(key in full for key in ('one-plus-one', 'two-plus-one'))
            else:
                assert all(key in test['comment'] for key in ('one-plus-one', 'two-plus-one'))
            if name == 'hooks':
                assert payload['info']['revision'] == 'tutorial-revision'
                assert len(test['evidences']) == 2
    assert seen == [
        'basic',
        'local',
        'inspect',
        'values',
        'redact',
        'failure',
        'xray',
        'comments',
        'archive',
        'preupload',
        'inspect_xray',
        'parallel',
        'retries',
        'hooks',
    ], seen
    print(
        'PASS: all 14 README commands, JSON excerpt, intentional failure, restored passing cases, '
        'values/redaction, Xray comments/archive, parallel/retries and hooks; HTTP blocked'
    )

if len(sys.argv) > 2:
    wheel = Path(sys.argv[2])
    with zipfile.ZipFile(wheel) as archive:
        metadata_path = next(n for n in archive.namelist() if n.endswith('.dist-info/METADATA'))
        metadata = email.parser.BytesParser().parsebytes(archive.read(metadata_path))
        assert metadata['Description-Content-Type'] == 'text/markdown'
        assert metadata.get_payload(decode=True).decode('utf-8').strip() == readme.strip()
    from readme_renderer.markdown import render

    html = render(readme)
    assert html and '<table>' in html and 'test_add_one' in html
    assert 'Troubleshooting and migration' in html and 'All package options' in html
    assert '2. Run two input cases' in html and 'pytest_exit_status' in html
    assert '<script' not in html
    anchors = set(re.findall(r'id="([^"]+)"', html))
    assert all(link in anchors for link in re.findall(r'href="#([^"]+)"', html))
    assert all(link.startswith(('https://', '#')) for link in re.findall(r'href="([^"]+)"', html))
    (wheel.parent / 'README-preview.html').write_text(html)
    print('PASS: complete tutorial in wheel metadata and PyPI Markdown rendering')
