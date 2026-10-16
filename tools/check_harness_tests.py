"""Run the stdlib harness suite, rejecting an empty discovery result."""

import sys
import unittest
from pathlib import Path


def run(directory):
    suite = unittest.TestLoader().discover(str(directory), pattern='test_*.py')
    if suite.countTestCases() == 0:
        print('Harness blocked: no tests discovered', file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return int(not result.wasSuccessful() or result.testsRun <= len(result.skipped))


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    raise SystemExit(run(root / 'tests/agent'))
