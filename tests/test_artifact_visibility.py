"""Exercise the exact workflow guard without network calls or real artifacts."""

import copy
import io
import json
import textwrap
import urllib.error
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github/workflows/tests.yml').read_text()
SCRIPT = textwrap.dedent(WORKFLOW.split("<<'PYTHON_ARTIFACT_VISIBILITY'\n", 1)[1].split(
    '          PYTHON_ARTIFACT_VISIBILITY', 1)[0])
GOOD = {'total_count': 1, 'artifacts': [{
    'id': 12, 'name': 'release-distributions-python-3.12-attempt-2', 'expired': False,
    'digest': 'sha256:' + 'b' * 64,
    'workflow_run': {'id': 34, 'repository_id': 56, 'head_sha': 'a' * 40},
}]}


@pytest.fixture
def guard(monkeypatch):
    values = {'EXPECTED_ARTIFACT_ID': '12', 'EXPECTED_ARTIFACT_DIGEST': 'b' * 64,
              'EXPECTED_ARTIFACT_NAME': 'release-distributions-python-3.12-attempt-2',
              'EXPECTED_HEAD_SHA': 'a' * 40, 'GITHUB_RUN_ID': '34', 'GITHUB_REPOSITORY_ID': '56',
              'GITHUB_REPOSITORY': 'synthetic/repo'}
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    sleep = Mock()
    monkeypatch.setattr('time.sleep', sleep)

    def run(responses):
        opening = Mock(side_effect=[io.BytesIO(json.dumps(x).encode()) if isinstance(x, dict) else x
                                    for x in responses])
        monkeypatch.setattr('urllib.request.urlopen', opening)
        return opening, sleep, lambda: exec(compile(SCRIPT, 'tests.yml visibility guard', 'exec'), {})

    return run


def test_exact_metadata_returns_immediately_without_auth(guard):
    opening, sleep, run = guard([GOOD])
    run()
    opening.assert_called_once()
    request = opening.call_args.args[0]
    assert request.full_url.startswith('https://api.github.com/repos/synthetic/repo/actions/runs/34/artifacts?')
    assert 'attempt-2' in request.full_url
    assert 'Authorization' not in request.headers
    assert opening.call_args.kwargs == {'timeout': 5}
    sleep.assert_not_called()


def test_only_successful_empty_metadata_is_retried(guard):
    opening, sleep, run = guard([{'total_count': 0, 'artifacts': []}] * 2 + [GOOD])
    run()
    assert opening.call_count == 3
    assert [x.args for x in sleep.call_args_list] == [(2,), (2,)]


def test_missing_metadata_has_short_fixed_bound(guard):
    opening, sleep, run = guard([{'total_count': 0, 'artifacts': []}] * 4)
    with pytest.raises(RuntimeError, match='four checks'):
        run()
    assert opening.call_count == 4 and sleep.call_count == 3


@pytest.mark.parametrize('status', [401, 403, 404, 410, 429, 500, 503])
def test_http_errors_are_never_retried(guard, status):
    error = urllib.error.HTTPError('https://api.github.com/synthetic', status, 'synthetic failure', {}, None)
    opening, sleep, run = guard([error, GOOD])
    with pytest.raises(urllib.error.HTTPError) as result:
        run()
    assert result.value.code == status
    opening.assert_called_once()
    sleep.assert_not_called()


@pytest.mark.parametrize('error', [TimeoutError('timeout'), urllib.error.URLError('TLS validation failed'),
                                  json.JSONDecodeError('invalid JSON', '', 0)])
def test_transport_and_json_errors_are_never_retried(guard, error):
    opening, sleep, run = guard([error, GOOD])
    with pytest.raises(type(error)):
        run()
    opening.assert_called_once()
    sleep.assert_not_called()


@pytest.mark.parametrize('field,value', [('id', 13), ('name', 'other'), ('expired', True),
                                        ('digest', 'sha256:' + 'c' * 64), ('run.id', 35),
                                        ('run.repository_id', 57), ('run.head_sha', 'c' * 40)])
def test_wrong_identity_provenance_or_digest_is_terminal(guard, field, value):
    data = copy.deepcopy(GOOD)
    target = data['artifacts'][0]
    if field.startswith('run.'):
        target = target['workflow_run']
        field = field[4:]
    target[field] = value
    opening, sleep, run = guard([data, GOOD])
    with pytest.raises(RuntimeError, match='mismatch'):
        run()
    opening.assert_called_once()
    sleep.assert_not_called()


@pytest.mark.parametrize('data', [{'total_count': 1, 'artifacts': []},
                                 {'total_count': 2, 'artifacts': GOOD['artifacts'] * 2},
                                 {'total_count': 0, 'artifacts': {}}])
def test_incomplete_or_ambiguous_metadata_is_terminal(guard, data):
    opening, sleep, run = guard([data, GOOD])
    with pytest.raises(RuntimeError, match='Ambiguous'):
        run()
    opening.assert_called_once()
    sleep.assert_not_called()


def test_pinned_downloader_exact_id_and_checksums_remain():
    handoff = WORKFLOW.split('      - name: Smoke-test publisher artifact download without publishing', 1)[1]
    assert 'actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333' in handoff
    assert 'artifact-ids: ${{ steps.distributions.outputs.artifact-id }}' in handoff
    assert 'assert {p.name for p in root.iterdir()} == set(expected)' in handoff
    assert 'hashlib.sha256(path.read_bytes()).hexdigest() == digest' in handoff
    assert 'continue-on-error' not in WORKFLOW
    assert 'permissions:\n  contents: read\n' in WORKFLOW
    publisher = (ROOT / '.github/workflows/publish.yml').read_text()
    triggers = publisher.split('permissions:', 1)[0]
    assert 'workflow_dispatch:' in triggers and 'push:' not in triggers and 'workflow_run:' not in triggers
