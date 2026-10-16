"""Collection behavior and deterministic scaling; no server or clock thresholds."""

import json
from types import SimpleNamespace

import pytest

from pytest_xray.exceptions import XrayError
from pytest_xray.xray_plugin import XrayPlugin


def plugin(allow=False):
    instance = object.__new__(XrayPlugin)
    instance.allow_duplicate_ids = allow
    return instance


def item(*keys):
    marker = SimpleNamespace(args=keys, kwargs={})
    return SimpleNamespace(nodeid='synthetic', get_closest_marker=lambda name: marker)


class CountedKey(str):
    comparisons = 0

    def __hash__(self):
        # Distinct deterministic hashes isolate lookup complexity from collisions.
        return int(self.split('-')[1])

    def __eq__(self, other):
        type(self).comparisons += 1
        return super().__eq__(other)


@pytest.mark.parametrize('allow', [False, True])
@pytest.mark.parametrize('size', [128, 256, 512])
def test_unique_key_comparisons_are_bounded(allow, size):
    items = [item(CountedKey(f'DEMO-{n}')) for n in range(size)]
    CountedKey.comparisons = 0
    plugin(allow)._verify_jira_ids_for_items(items)
    assert CountedKey.comparisons <= size * 4


def test_duplicate_diagnostic_keeps_marker_order_and_stops_at_first_item():
    items = [item('DEMO-1', 'DEMO-2'), item('DEMO-2', 'DEMO-1', 'DEMO-2'), item(None)]
    with pytest.raises(XrayError) as caught:
        plugin()._verify_jira_ids_for_items(items)
    assert caught.value.message == "Duplicated test case ids: ['DEMO-2', 'DEMO-1']"


@pytest.mark.parametrize('allow', [False, True])
def test_repeated_key_in_single_marker_is_not_a_duplicate(allow):
    instance = plugin(allow)
    repeated = item('DEMO-2', 'DEMO-1', 'DEMO-2')
    assert instance._get_test_keys(repeated) == ['DEMO-2', 'DEMO-1']
    instance._verify_jira_ids_for_items([repeated])


def test_allow_duplicates_still_validates_later_markers():
    with pytest.raises(XrayError, match='nonempty string test keys'):
        plugin(True)._verify_jira_ids_for_items([item('DEMO-1'), item('DEMO-1'), item('')])


@pytest.mark.parametrize('workers', [[], ['-n', '2']])
def test_allowed_duplicate_cases_keep_grouping_and_key_order(pytester, workers):
    pytester.makepyfile('''
import pytest
@pytest.mark.xray('DEMO-2', 'DEMO-1', 'DEMO-2')
@pytest.mark.parametrize('value', [1, 2])
def test_case(value):
    assert value > 0
''')
    result = pytester.runpytest('--jira-xray', '--allow-duplicate-ids', '--xraypath=preview.json', *workers)
    result.assert_outcomes(passed=2)
    data = json.loads((pytester.path / 'preview.json').read_text())
    assert [test['testKey'] for test in data['tests']] == ['DEMO-2', 'DEMO-1']
    assert [test['status'] for test in data['tests']] == ['PASS', 'PASS']
