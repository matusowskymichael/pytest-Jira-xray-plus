"""Synthetic offline demo; never imports anything into Jira (Apache-2.0)."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

source = Path(__file__).resolve().parents[1] / 'src'
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / 'conftest.py').write_text('''
import requests
import socket
def blocked(*args, **kwargs):
    raise AssertionError('Offline demo: network forbidden')
requests.sessions.Session.request = blocked
socket.socket.connect = blocked
socket.create_connection = blocked
''')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('XRAY_', 'PYTEST_'))}
    env.update(PYTHONPATH=str(source), PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    for label, values in [('forward', [0, 1]), ('reverse', [1, 0])]:
        (root / 'test_demo.py').write_text('''
import pytest
@pytest.mark.xray('SYN-1')
@pytest.mark.parametrize('value', VALUES, ids=lambda value: 'case-a' if value == 0 else 'case-b')
def test_demo(value):
    assert value == 1
'''.replace('VALUES', repr(values)))
        result = subprocess.run([
            sys.executable, '-m', 'pytest', '-p', 'pytest_xray.plugin',
            '--xray-case-report=cases.json', '--jira-xray', '--allow-duplicate-ids',
            '--xray-parameter-details', '--xraypath=xray.json', '-q',
        ], cwd=root, env=env, capture_output=True, text=True)
        if result.returncode != 1:
            raise RuntimeError(result.stdout + result.stderr)
        report = json.loads((root / 'cases.json').read_text())
        tests = json.loads((root / 'xray.json').read_text())['tests']
        cases = report['cases']
        assert report['pytest_exit_status'] == 1 and len(cases) == 2
        assert [case['status'] for case in cases] == ['failed', 'passed']
        assert [case['attempts'][0]['parameter_id'] for case in cases] == ['case-a', 'case-b']
        assert all(len(case['attempts']) == 1 for case in cases)
        assert all('parameter_values' not in case['attempts'][0] for case in cases)
        assert len(tests) == 1 and tests[0]['status'] == 'FAIL'
        assert all(name in tests[0]['comment'] for name in ('case-a', 'case-b'))
        print(f'{label}: case-a=failed, case-b=passed; pytest_exit_status=1; Xray JSON status=FAIL')
    print('PASS: both cases retained in both orders; comments retained; no Jira request made.')
    print('Native iterations: NOT tested. Temporary reports removed.')
