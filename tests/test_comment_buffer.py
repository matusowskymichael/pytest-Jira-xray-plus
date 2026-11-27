"""Comment aggregation retains the public string and serialization contract."""

import copy
import json
import os
import pickle

import pytest

from pytest_xray.comment_limits import bound_comments
from pytest_xray.helper import STATUS_STR_MAPPER_CLOUD, Status, TestCase

SEPARATOR = '\n' + '-' * 80 + '\n'
PREFIX = '{noformat:borderWidth=0px|bgColor=transparent}'


@pytest.mark.parametrize('fragments', [[], [''], ['one'], ['', 'one', '', 'two', ''], ['界', '🙂', 'a\nb']])
def test_comment_output_and_repeated_serialization(fragments):
    case = TestCase('SYN-1', Status.PASS)
    for text in fragments:
        case.merge(TestCase('SYN-1', Status.PASS, text))
    expected = SEPARATOR.join(x for x in fragments if x)
    data = {'testKey': 'SYN-1', 'status': 'PASS'}
    if expected:
        data['comment'] = PREFIX + expected + '{noformat}'
    assert case.comment == expected
    assert case.as_dict() == data == case.as_dict()
    case.merge(TestCase('SYN-1', Status.PASS, 'tail'))
    assert case.comment == (expected + SEPARATOR if expected else '') + 'tail'


def test_assignment_discards_pending_comments_and_augmented_assignment_works():
    case = TestCase('SYN-1', Status.PASS, 'old')
    case.merge(TestCase('SYN-1', Status.PASS, 'pending'))
    case.comment = 'replacement'
    case.comment += ' suffix'
    case.merge(TestCase('SYN-1', Status.PASS, 'tail'))
    assert case.comment == 'replacement suffix' + SEPARATOR + 'tail'
    case.comment = ''
    assert 'comment' not in case.as_dict()
    case.merge(TestCase('SYN-1', Status.PASS, 'new'))
    assert case.comment == 'new'


def test_self_merge_and_merged_source_snapshot():
    case = TestCase('SYN-1', Status.PASS, 'a')
    case.merge(TestCase('SYN-1', Status.PASS, 'b'))
    target = TestCase('SYN-1', Status.PASS)
    target.merge(case)
    case.merge(case)
    assert case.comment == SEPARATOR.join(['a', 'b', 'a', 'b', ''])
    assert target.comment == SEPARATOR.join(['a', 'b'])


def test_subclass_comment_descriptor_still_observes_legacy_assignments():
    class CustomCase(TestCase):
        @property
        def comment(self):
            return self.text

        @comment.setter
        def comment(self, value):
            self.text = value
            self.assignments = getattr(self, 'assignments', []) + [value]

    case = CustomCase('SYN-1', Status.PASS, 'a')
    case.merge(TestCase('SYN-1', Status.PASS, 'b'))
    assert case.assignments == ['a', 'a' + SEPARATOR, 'a' + SEPARATOR + 'b']
    assert case.as_dict()['comment'] == PREFIX + 'a' + SEPARATOR + 'b{noformat}'


def test_status_evidence_defects_and_archive_bytes(tmp_path):
    case = TestCase('SYN-1', Status.PASS, '界' * 100, STATUS_STR_MAPPER_CLOUD,
                    [{'filename': 'a', 'data': 'YQ=='}], ['BUG-1'])
    case.merge(TestCase('SYN-1', Status.FAIL, '🙂' * 100,
                        evidences=[{'filename': 'b', 'data': 'Yg=='}], defects=['BUG-1', 'BUG-2']))
    expected = {'testKey': 'SYN-1', 'status': 'FAILED',
                'comment': PREFIX + '界' * 100 + SEPARATOR + '🙂' * 100 + '{noformat}',
                'evidences': [{'filename': 'a', 'data': 'YQ=='}, {'filename': 'b', 'data': 'Yg=='}],
                'defects': ['BUG-1', 'BUG-2']}
    assert case.as_dict() == expected
    full = {'tests': [case.as_dict()]}
    reference = {'tests': [expected]}
    actual_path, expected_path = tmp_path / 'actual.json', tmp_path / 'expected.json'
    assert bound_comments(full, 256, str(actual_path)) == bound_comments(reference, 256, str(expected_path))
    assert actual_path.read_bytes() == expected_path.read_bytes()
    assert case.as_dict() == expected


def test_merge_rejects_other_key_without_mutation():
    case = TestCase('SYN-1', Status.PASS, 'a')
    before = copy.deepcopy(case.as_dict())
    with pytest.raises(ValueError):
        case.merge(TestCase('SYN-2', Status.FAIL, 'b'))
    assert case.as_dict() == before


def test_many_merges_defer_join_and_cache_materialized_string():
    case = TestCase('SYN-1', Status.PASS, 'first')
    for _ in range(1000):
        case.merge(TestCase('SYN-1', Status.PASS, 'fragment'))
    # Deterministic complexity guard: merges must not rebuild the growing prefix.
    assert case._comment == 'first'
    value = case.comment
    assert value == SEPARATOR.join(['first'] + ['fragment'] * 1000)
    assert case.comment is value
    assert case._comment_parts is None


@pytest.mark.parametrize('workers', [0, 2])
def test_cli_comments_follow_observed_arrival_and_hook_archive_contract(pytester, monkeypatch, workers):
    for name in list(os.environ):
        if name.startswith(('XRAY_', 'PYTEST_')):
            monkeypatch.delenv(name)
    pytester.makeconftest('''
        import json
        from pathlib import Path
        import pytest
        import requests
        def blocked(*args, **kwargs): raise AssertionError('HTTP prohibited')
        requests.sessions.Session.request = blocked
        arrivals = []
        @pytest.hookimpl(tryfirst=True)
        def pytest_runtest_logreport(report):
            if report.when == 'call' and report.passed:
                arrivals.append(report.capstdout)
        def pytest_xray_results(results, session):
            # The hook receives a materialized string before bounding/archival.
            assert isinstance(results['tests'][0]['comment'], str)
            results['tests'][0]['defects'] = ['HOOK-1']
            Path('hook.json').write_text(json.dumps(results))
            Path('arrivals.json').write_text(json.dumps(arrivals))
    ''')
    pytester.makepyfile('''
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('value', range(30))
        def test_case(value):
            print(f'fragment-{value:03d}-界')
    ''')
    result = pytester.runpytest_subprocess('-q', '-n', str(workers), '--jira-xray', '--xraypath=preview.json',
                                         '--allow-duplicate-ids', '--add-captures', '--xray-comment-limit=256',
                                         '--xray-full-report=full.json')
    result.assert_outcomes(passed=30)
    assert result.ret == 0
    def read(name):
        return json.loads((pytester.path / name).read_text())

    arrivals = read('arrivals.json')
    assert len(arrivals) == 30
    assert set(arrivals) == {f'fragment-{i:03d}-界\n' for i in range(30)}
    if not workers:
        assert arrivals == [f'fragment-{i:03d}-界\n' for i in range(30)]
    expected = PREFIX + SEPARATOR.join('-' * 29 + ' Captured stdout call ' + '-' * 29 + '\n' + s
                                       for s in arrivals) + '{noformat}'
    full = read('full.json')
    assert full == read('hook.json')
    assert full['tests'] == [{'testKey': 'SYN-1', 'status': 'PASS', 'comment': expected, 'defects': ['HOOK-1']}]
    reference_path = pytester.path / 'reference.json'
    bounded, count = bound_comments(full, 256, str(reference_path))
    assert count == 1 and read('preview.json') == bounded
    assert (pytester.path / 'full.json').read_bytes() == reference_path.read_bytes()


@pytest.mark.parametrize('clone', [copy.copy, copy.deepcopy, lambda x: pickle.loads(pickle.dumps(x))])
def test_copied_pending_comments_are_independent(clone):
    case = TestCase('SYN-1', Status.PASS, 'a')
    case.merge(TestCase('SYN-1', Status.PASS, 'b'))
    other = clone(case)
    case.merge(TestCase('SYN-1', Status.PASS, 'original'))
    other.merge(TestCase('SYN-1', Status.PASS, 'copy'))
    assert case.comment == SEPARATOR.join(['a', 'b', 'original'])
    assert other.comment == SEPARATOR.join(['a', 'b', 'copy'])


def test_incoming_subclass_descriptor_retains_legacy_reads():
    class IncomingCase(TestCase):
        @property
        def comment(self):
            self.reads += 1
            return f'fragment-{self.reads}'

        @comment.setter
        def comment(self, value):
            self.reads = 0

    case = TestCase('SYN-1', Status.PASS, 'first')
    incoming = IncomingCase('SYN-1', Status.PASS)
    case.merge(incoming)
    assert incoming.reads == 2
    assert case.comment == 'first' + SEPARATOR + 'fragment-2'
