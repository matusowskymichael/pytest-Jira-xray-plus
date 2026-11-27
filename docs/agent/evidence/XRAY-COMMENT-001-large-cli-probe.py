"""Matched installed pytest CLI probes; xdist order is checked, never normalized.

Usage: python tools/benchmark_comment_cli.py BASELINE_PYTHON CANDIDATE_PYTHON
"""

import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SEPARATOR = '\n' + '-' * 80 + '\n'
PREFIX = '{noformat:borderWidth=0px|bgColor=transparent}'
HEADER = '-' * 29 + ' Captured stdout call ' + '-' * 29 + '\n'
CONFTEST = '''
import json
from pathlib import Path
import pytest
import requests
def blocked(*a, **kw): raise AssertionError('HTTP prohibited')
requests.sessions.Session.request = blocked
arrivals = []
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.when == 'call' and report.passed:
        arrivals.append(report.capstdout)
def pytest_xray_results(results, session):
    Path('arrivals.json').write_text(json.dumps(arrivals))
    Path('hook.json').write_text(json.dumps(results))
'''


def normalize_dates(data):
    result = json.loads(json.dumps(data))
    for key in ['startDate', 'finishDate']:
        result.get('info', {}).pop(key, None)
    return result


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('XRAY_', 'PYTEST_', 'PYTHONPATH'))}
    rows = []
    for count, captures in [(10000, True)]:
        for workers in [0, 2]:
            records = []
            serial_reference = None
            with tempfile.TemporaryDirectory(prefix='xray-cli-') as directory:
                root = Path(directory)
                (root / 'conftest.py').write_text(CONFTEST)
                (root / 'test_sample.py').write_text(
                    "import pytest\n@pytest.mark.xray('SYN-1')\n"
                    f"@pytest.mark.parametrize('i', range({count}))\n"
                    "def test_case(i):\n    print(f'{i:05d}:' + 'x' * 189)\n"
                )
                for python in sys.argv[1:]:
                    times = []
                    for _ in range(3):
                        # Distinct outputs each invocation; stale output cannot satisfy a probe.
                        for name in ['preview.json', 'full.json', 'hook.json', 'arrivals.json']:
                            (root / name).unlink(missing_ok=True)
                        argv = [python, '-m', 'pytest', '-q', '-n', str(workers), '--jira-xray',
                                '--xraypath=preview.json', '--allow-duplicate-ids', '--xray-comment-limit=256',
                                '--xray-full-report=full.json']
                        if captures:
                            argv.append('--add-captures')
                        start = time.perf_counter()
                        run = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=120)
                        times.append((time.perf_counter() - start) * 1000)
                        if run.returncode or f'{count} passed' not in run.stdout:
                            raise RuntimeError(run.stdout + run.stderr)
                        arrivals = json.loads((root / 'arrivals.json').read_text())
                        expected_inputs = [f'{i:05d}:' + 'x' * 189 + '\n' for i in range(count)]
                        if len(arrivals) != count or set(arrivals) != set(expected_inputs):
                            raise RuntimeError('Missing or repeated arrival fragment')
                        if workers == 0 and arrivals != expected_inputs:
                            raise RuntimeError('Serial order changed')
                        full = json.loads((root / 'full.json').read_text())
                        expected = {'testKey': 'SYN-1', 'status': 'PASS'}
                        if captures:
                            expected['comment'] = PREFIX + SEPARATOR.join(HEADER + s for s in arrivals) + '{noformat}'
                        if full['tests'] != [expected] or full != json.loads((root / 'hook.json').read_text()):
                            raise RuntimeError('Full dictionary or observed arrival order changed')
                        normalized = normalize_dates(full)
                        if workers == 0:
                            if serial_reference is None:
                                serial_reference = normalized
                            elif normalized != serial_reference:
                                raise RuntimeError('Serial baseline/candidate differs beyond timestamps')
                    records.append({'python': python, 'ms': times, 'median_ms': statistics.median(times)})
            rows.append({'cases': count, 'captures': captures, 'workers': workers, 'measurements': records,
                         'verification': 'Exact observed fragment order and full hook dictionary; '
                                         'serial baseline/candidate equal after timestamp-only normalization'})
    print(json.dumps({'scope': 'Installed pytest CLI including startup, collection, execution and offline files',
                      'no_http': True, 'workloads': rows}, indent=2))


if __name__ == '__main__':
    main()
