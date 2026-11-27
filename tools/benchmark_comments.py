"""Compare isolated TestCase merge + materialization under one interpreter.

Usage: python tools/benchmark_comments.py BASELINE_SRC CANDIDATE_SRC
Not an end-to-end pytest/Xray benchmark. Public synthetic fragments only.
"""

import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path


def worker(source):
    sys.path.insert(0, str(Path(source).resolve()))
    from pytest_xray.helper import Status, TestCase

    results = []
    for size, empty, batches in [(1, False, 1000), (10, False, 100), (10000, True, 1), (10000, False, 1)]:
        texts = ['' if empty else f'{i:05d}:' + 'x' * 189 for i in range(size)]
        timings = []
        for _ in range(5):
            start = time.perf_counter()
            for _ in range(batches):
                case = TestCase('SYN-1', Status.PASS)
                for text in texts:
                    case.merge(TestCase('SYN-1', Status.PASS, text))
                data = case.as_dict()
            timings.append((time.perf_counter() - start) * 1000 / batches)
        results.append({'fragments': size, 'empty': empty, 'batches': batches,
                        'ms': timings, 'median_ms': statistics.median(timings), 'data': data})
    return results


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        print(json.dumps(worker(sys.argv[2])))
        return
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    measurements = []
    for source in sys.argv[1:]:
        raw = subprocess.check_output([sys.executable, __file__, '--worker', source], text=True)
        measurements.append(json.loads(raw))
    rows = []
    for baseline, candidate in zip(*measurements):
        if baseline['data'] != candidate['data']:
            raise RuntimeError('Entire TestCase dictionary differs')
        digest = hashlib.sha256(json.dumps(baseline['data'], sort_keys=True).encode()).hexdigest()
        rows.append({'fragments': baseline['fragments'], 'empty': baseline['empty'],
                     'fragment_ascii_characters': 195, 'repetitions': 5, 'batches': baseline['batches'],
                     'baseline_ms': baseline['ms'], 'candidate_ms': candidate['ms'],
                     'baseline_median_ms': baseline['median_ms'], 'candidate_median_ms': candidate['median_ms'],
                     'entire_dictionary_equal': True, 'dictionary_sha256': digest})
    print(json.dumps({'python': sys.version, 'platform': platform.platform(),
                      'sources': sys.argv[1:], 'scope': 'Isolated merge plus as_dict; not end-to-end',
                      'workloads': rows}, indent=2))


if __name__ == '__main__':
    main()
