"""Matched, warmed, interleaved no-capture CLI controls (no HTTP)."""

import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: benchmark_comment_controls.py BASELINE_PYTHON CANDIDATE_PYTHON')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('XRAY_', 'PYTEST_', 'PYTHONPATH'))}
    workloads = []
    for count in [1, 1000, 10000]:
        for workers in [0, 2]:
            with tempfile.TemporaryDirectory(prefix='comment-controls-') as directory:
                root = Path(directory)
                (root / 'conftest.py').write_text(
                    "import requests\ndef blocked(*a, **kw): raise AssertionError('HTTP prohibited')\n"
                    "requests.sessions.Session.request = blocked\n"
                )
                (root / 'test_control.py').write_text(
                    "import pytest\n@pytest.mark.xray('SYN-1')\n"
                    f"@pytest.mark.parametrize('i', range({count}))\n"
                    "def test_case(i):\n    print(f'{i:05d}:' + 'x' * 189)\n"
                )
                reference = None

                def run(python, root=root, workers=workers, count=count):
                    nonlocal reference
                    target = root / 'preview.json'
                    target.unlink(missing_ok=True)
                    args = [python, '-m', 'pytest', '-q', '-n', str(workers), '--jira-xray',
                            '--xraypath=preview.json', '--allow-duplicate-ids']
                    start = time.perf_counter()
                    result = subprocess.run(args, cwd=root, env=env, capture_output=True, text=True, timeout=120)
                    milliseconds = (time.perf_counter() - start) * 1000
                    if result.returncode or f'{count} passed' not in result.stdout:
                        raise RuntimeError(result.stdout + result.stderr)
                    data = json.loads(target.read_text())
                    if data['tests'] != [{'testKey': 'SYN-1', 'status': 'PASS'}]:
                        raise RuntimeError('No-capture payload changed')
                    for key in ['startDate', 'finishDate']:
                        data.get('info', {}).pop(key, None)
                    if reference is None:
                        reference = data
                    elif reference != data:
                        raise RuntimeError('Payload differs after timestamp-only normalization')
                    return milliseconds

                for python in sys.argv[1:]:
                    run(python)  # Untimed warm-up for both installations.
                pairs = []
                for i in range(7):
                    order = [0, 1] if i % 2 == 0 else [1, 0]
                    times = {}
                    for index in order:
                        times[index] = run(sys.argv[index + 1])
                    pairs.append({'order': order, 'baseline_ms': times[0], 'candidate_ms': times[1],
                                  'candidate_delta_percent': 100 * (times[1] / times[0] - 1)})
                workloads.append({'cases': count, 'workers': workers, 'captures': False, 'pairs': pairs,
                                  'baseline_median_ms': statistics.median(x['baseline_ms'] for x in pairs),
                                  'candidate_median_ms': statistics.median(x['candidate_ms'] for x in pairs),
                                  'paired_delta_median_percent': statistics.median(
                                      x['candidate_delta_percent'] for x in pairs),
                                  'payload_equal_after_timestamp_only_normalization': True})
    print(json.dumps({'python_paths': sys.argv[1:], 'warmups_per_environment': 1,
                      'protocol': 'Seven AB/BA alternating pairs per workload, sequential, HTTP blocked',
                      'workloads': workloads}, indent=2))


if __name__ == '__main__':
    main()
