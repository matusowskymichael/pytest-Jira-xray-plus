"""Run against a selected source tree; fail if passing parameter detail is lost.

python tools/reproduce.py ../upstream/src
python tools/reproduce.py src --details
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

source = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / 'test_synthetic.py').write_text("""
import pytest
@pytest.mark.xray('SYN-1')
@pytest.mark.parametrize('value', [10, 20])
def test_case(value):
    assert value > 0
@pytest.mark.xray('SYN-2')
@pytest.mark.parametrize('value', [0, 1])
def test_mixed(value):
    assert value == 1
""")
    (root / 'conftest.py').write_text("""
import requests
def blocked(*args, **kwargs):
    raise AssertionError('Offline probe: network transport forbidden')
requests.sessions.Session.request = blocked
""")
    env = {key: value for key, value in os.environ.items() if not key.startswith('XRAY_')}
    env.update(PYTHONPATH=str(source), PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    args = [
        sys.executable,
        '-m',
        'pytest',
        '-p',
        'pytest_xray.plugin',
        '--jira-xray',
        '--allow-duplicate-ids',
        '--xraypath=xray.json',
        '-q',
    ]
    if '--details' in sys.argv:
        args.append('--xray-parameter-details')
    result = subprocess.run(args, cwd=root, env=env, capture_output=True, text=True)
    print(result.stdout)
    assert result.returncode == 1, result.stderr
    tests = json.loads((root / 'xray.json').read_text())['tests']
    print(json.dumps(tests, indent=2))
    assert tests[1]['status'] == 'FAIL', 'Failure overwritten by later pass'
    print('Confirmed: first failure survives later pass.')
    assert 'test_case[10]' in tests[0].get('comment', ''), 'Parameter case 10 is not represented'
    assert 'test_case[20]' in tests[0]['comment'], 'Parameter case 20 is not represented'
    print('Confirmed: both passing parameter cases are represented.')
