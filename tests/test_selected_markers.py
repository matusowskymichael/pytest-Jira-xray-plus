"""Validate runnable Xray cases after pytest's normal selection filters."""

import json

import pytest


@pytest.mark.parametrize('workers', [0, 2])
@pytest.mark.parametrize('selection', [['-k', 'chosen'], ['-m', 'selected']])
@pytest.mark.parametrize('excluded_marker', ["'DEMO-1'", "''", "'DEMO-2', defects='invalid'"])
def test_deselected_cases_do_not_block_selected_case(pytester, workers, selection, excluded_marker):
    pytester.makeini('[pytest]\nmarkers = selected: synthetic selection marker\n')
    pytester.makepyfile(f'''
import pytest
@pytest.mark.parametrize('value', [
    pytest.param(1, id='chosen', marks=[pytest.mark.selected, pytest.mark.xray('DEMO-1')]),
    pytest.param(2, id='excluded', marks=pytest.mark.xray({excluded_marker})),
])
def test_case(value):
    assert value == 1
''')
    result = pytester.runpytest_subprocess(
        '--jira-xray', '--xraypath=preview.json', '-n', str(workers), *selection
    )
    result.assert_outcomes(passed=1)
    assert result.ret == 0
    tests = json.loads((pytester.path / 'preview.json').read_text())['tests']
    assert tests == [{'testKey': 'DEMO-1', 'status': 'PASS'}]


@pytest.mark.parametrize('workers', [0, 2])
def test_selected_duplicates_still_block_before_fixtures(pytester, workers):
    pytester.makepyfile('''
from pathlib import Path
import pytest
@pytest.fixture(autouse=True)
def check_not_run():
    Path('fixture-ran').touch()
@pytest.mark.xray('DEMO-1')
@pytest.mark.parametrize('value', [1, 2], ids=['chosen-one', 'chosen-two'])
def test_case(value): pass
''')
    result = pytester.runpytest_subprocess(
        '--jira-xray', '--xraypath=preview.json', '-n', str(workers), '-k', 'chosen'
    )
    assert result.ret in (pytest.ExitCode.INTERRUPTED, pytest.ExitCode.TESTS_FAILED)
    assert 'Duplicated test case ids' in result.stdout.str()
    assert not (pytester.path / 'fixture-ran').exists()
    assert json.loads((pytester.path / 'preview.json').read_text())['tests'] == []
