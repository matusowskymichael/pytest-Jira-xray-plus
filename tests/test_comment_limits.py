"""A client policy must never silently discard the full payload."""

import json

import pytest

from pytest_xray.comment_limits import TRUNCATION_NOTICE, bound_comments
from pytest_xray.exceptions import XrayError


@pytest.mark.parametrize('text', ['x' * 1000, '🙂' * 1000, '{noformat:borderWidth=0px}' + '界' * 1000 + '{noformat}'])
def test_bounded_comment_preserves_full_archive_and_input(tmp_path, text):
    full = tmp_path / 'full.json'
    data = {'tests': [{'testKey': 'SYN-1', 'status': 'FAIL', 'comment': text, 'evidences': [{'data': 'synthetic'}]}]}
    bounded, count = bound_comments(data, 256, str(full))
    assert count == 1
    assert len(bounded['tests'][0]['comment'].encode('utf-8')) <= 256
    assert TRUNCATION_NOTICE in bounded['tests'][0]['comment']
    if text.startswith('{noformat:'):
        assert bounded['tests'][0]['comment'].endswith('{noformat}')
    assert data['tests'][0]['comment'] == text
    assert json.loads(full.read_text()) == data
    assert bounded['tests'][0]['status'] == 'FAIL'
    assert bounded['tests'][0]['evidences'] == data['tests'][0]['evidences']


def test_limit_is_bytes_and_exact_boundary_is_unchanged(tmp_path):
    data = {'tests': [{'comment': '🙂' * 64}, {'status': 'PASS'}]}
    bounded, count = bound_comments(data, 256, None)
    assert (bounded, count) == (data, 0)
    with pytest.raises(XrayError, match='complete payload'):
        bound_comments({'tests': [{'comment': '🙂' * 65}]}, 256, None)


def test_archive_write_failure_prevents_truncation(tmp_path):
    parent = tmp_path / 'file'
    parent.write_text('keep')
    with pytest.raises(XrayError):
        bound_comments({'tests': [{'comment': 'x' * 1000}]}, 256, str(parent / 'full.json'))
    assert parent.read_text() == 'keep'


@pytest.mark.parametrize('workers', [0, 2])
def test_opt_in_archive_and_visible_truncation(pytester, workers):
    pytester.makepyfile("""
        import pytest
        @pytest.mark.xray('SYN-1')
        @pytest.mark.parametrize('text', ['界' * 1000], ids=['safe'])
        def test_case(text): pass
    """)
    args = [
        '-n',
        str(workers),
        '--jira-xray',
        '--xraypath=xray.json',
        '--xray-comment-limit=256',
        '--xray-parameter-details',
        '--xray-case-report=cases.json',
    ]
    result = pytester.runpytest_subprocess(*args)
    assert result.ret == 3
    assert not (pytester.path / 'xray.json').exists()
    assert 'export withheld' in result.stdout.str()
    result = pytester.runpytest_subprocess(*args, '--xray-full-report=full.json')
    assert result.ret == 0
    assert 'truncated 1 comment(s)' in result.stdout.str()
    full = json.loads((pytester.path / 'full.json').read_text())
    bounded = json.loads((pytester.path / 'xray.json').read_text())
    assert len(full['tests'][0]['comment'].encode()) > 256
    assert len(bounded['tests'][0]['comment'].encode()) <= 256
    assert len(json.loads((pytester.path / 'cases.json').read_text())['cases']) == 1


@pytest.mark.parametrize(
    'args',
    [
        ['--xray-comment-limit=255'],
        ['--xray-full-report=full.json'],
        ['--jira-xray', '--xraypath=same.json', '--xray-full-report=same.json'],
        ['--jira-xray', '--xray-case-report=same.json', '--xray-full-report=same.json'],
    ],
)
def test_invalid_policy_options_are_usage_errors(pytester, args):
    pytester.makepyfile('def test_ok(): pass')
    assert pytester.runpytest_subprocess(*args).ret == 4
