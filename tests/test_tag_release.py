"""Synthetic publication API: never send a request or create real tags/releases."""

import base64
import copy
import importlib.util
import io
import json
import urllib.error
import zipfile
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('tag_release', Path(__file__).parents[1] / 'tools/tag_release.py')
assert SPEC is not None and SPEC.loader is not None
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
COMMIT = 'a' * 40


class Fake:
    def __init__(self):
        self.run = {
            'path': '.github/workflows/publish.yml',
            'event': 'workflow_dispatch',
            'head_branch': 'main',
            'head_repository': {'full_name': release.REPO},
            'head_sha': COMMIT,
            'status': 'completed',
            'conclusion': 'success',
        }
        self.jobs = {
            'total_count': 2,
            'jobs': [{'name': 'build', 'conclusion': 'success'}, {'name': 'publish', 'conclusion': 'success'}],
        }
        self.source = {
            'pyproject.toml': '[project]\nname="pytest-jira-xray-plus"\nversion="1.2.3"\n',
            'CHANGELOG.rst': 'Unreleased\n==========\n- Later work.\n\n1.2.3 [2026-10-16]\n==================\n'
            '- The exact released fix.\n\n1.2.2 [2026-10-15]\n==================\n- Old fix.\n',
        }
        self.files = {
            'pytest_jira_xray_plus-1.2.3-py3-none-any.whl': b'wheel',
            'pytest_jira_xray_plus-1.2.3.tar.gz': b'sdist',
        }
        self.archive = self.zip(self.files)
        self.artifacts = {
            'total_count': 1,
            'artifacts': [
                {
                    'id': 7,
                    'name': 'verified-distributions',
                    'expired': False,
                    'digest': 'sha256:' + release.sha(self.archive),
                }
            ],
        }
        self.pypi = {
            'info': {'version': '1.2.3'},
            'urls': [
                {
                    'filename': name,
                    'digests': {'sha256': release.sha(data)},
                    'yanked': False,
                    'url': 'https://files.pythonhosted.org/' + name,
                }
                for name, data in self.files.items()
            ],
        }
        self.tag = None
        self.existing = None
        self.assets = []
        self.mutations = []
        self.upload_fail = False

    @staticmethod
    def zip(files):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as z:
            for name, data in files.items():
                z.writestr(name, data)
        return stream.getvalue()

    def api(self, path, method='GET', body=None, missing=False, raw=False):
        if method != 'GET':
            self.mutations.append((method, path, body))
            if path == '/git/refs':
                assert self.tag is None
                self.tag = body['sha']
                return {}
            if path == '/releases':
                self.existing = dict(body, id=8)
                return copy.deepcopy(self.existing)
            assert path == '/releases/8' and body == {'draft': False, 'make_latest': 'legacy'}
            self.existing['draft'] = False
            return copy.deepcopy(self.existing)
        if path == '/actions/runs/123':
            return self.run
        if path.endswith('/jobs?filter=latest&per_page=100'):
            return self.jobs
        if path.startswith('/contents/'):
            assert path.endswith('?ref=' + COMMIT)
            name = path.split('/contents/')[1].split('?')[0]
            return {'encoding': 'base64', 'content': base64.b64encode(self.source[name].encode()).decode()}
        if path.endswith('/artifacts?per_page=100'):
            return self.artifacts
        if path == '/actions/artifacts/7/zip':
            return self.archive
        if path == '/git/ref/tags/v1.2.3':
            return {'object': {'type': 'commit', 'sha': self.tag}} if self.tag else None
        if path.startswith('/releases?'):
            return [copy.deepcopy(self.existing)] if self.existing else []
        if path == '/releases/8':
            return copy.deepcopy(self.existing)
        if path == '/releases/8/assets?per_page=100':
            return copy.deepcopy(self.assets)
        raise AssertionError(path)

    def public(self, url):
        if url.endswith('/json'):
            return json.dumps(self.pypi).encode()
        return self.files[url.rsplit('/', 1)[1]]

    def upload(self, release_id, name, data):
        if self.upload_fail:
            raise release.ReleaseError('Synthetic upload failure')
        assert self.existing['draft'] and release_id == 8
        self.mutations.append(('upload', name, data))
        asset = {'name': name, 'state': 'uploaded', 'size': len(data), 'digest': 'sha256:' + release.sha(data)}
        self.assets.append(asset)
        return asset


def test_publication_and_no_op_retry():
    client = Fake()
    result = release.publish(client, '123')
    assert result['commit'] == COMMIT and result['tag'] == 'v1.2.3'
    assert client.tag == COMMIT and not client.existing['draft']
    assert len(client.assets) == 2
    assert 'exact released fix' in client.existing['body']
    assert 'Later work' not in client.existing['body'] and 'Old fix' not in client.existing['body']
    count = len(client.mutations)
    assert release.publish(client, '123') == result
    assert len(client.mutations) == count


def test_retry_resumes_matching_draft_after_upload_failure():
    client = Fake()
    client.upload_fail = True
    with pytest.raises(release.ReleaseError, match='upload failure'):
        release.publish(client, '123')
    assert client.tag == COMMIT and client.existing['draft']
    client.upload_fail = False
    release.publish(client, '123')
    assert not client.existing['draft']
    assert len([m for m in client.mutations if m[1] == '/git/refs']) == 1


@pytest.mark.parametrize(
    'field,value',
    [
        ('path', '.github/workflows/tests.yml'),
        ('event', 'pull_request'),
        ('head_branch', 'feature'),
        ('head_sha', 'main'),
        ('conclusion', 'failure'),
        ('status', 'in_progress'),
        ('head_repository', {'full_name': 'attacker/fork'}),
    ],
)
def test_untrusted_or_unsuccessful_run_never_writes(field, value):
    client = Fake()
    client.run[field] = value
    with pytest.raises(release.ReleaseError):
        release.publish(client, '123')
    assert not client.mutations


@pytest.mark.parametrize('state', ['failure', 'cancelled', 'skipped'])
def test_publication_job_gate(state):
    client = Fake()
    client.jobs['jobs'][1]['conclusion'] = state
    if state == 'skipped':
        assert release.publish(client, '123')['status'] == 'skipped'
    else:
        with pytest.raises(release.ReleaseError):
            release.publish(client, '123')
    assert not client.mutations


@pytest.mark.parametrize(
    'problem',
    [
        'expired',
        'ambiguous',
        'archive_hash',
        'extra_file',
        'pypi_hash',
        'pypi_files',
        'pypi_yanked',
        'pypi_version',
        'public_bytes',
        'changelog',
        'unstable_version',
        'job_pagination',
        'artifact_pagination',
        'tag_conflict',
    ],
)
def test_verification_failures_precede_all_writes(problem):
    client = Fake()
    if problem == 'expired':
        client.artifacts['artifacts'][0]['expired'] = True
    elif problem == 'ambiguous':
        client.artifacts['artifacts'] *= 2
        client.artifacts['total_count'] = 2
    elif problem == 'archive_hash':
        client.archive += b'changed'
    elif problem == 'extra_file':
        client.archive = client.zip({**client.files, '../payload': b'untrusted'})
        client.artifacts['artifacts'][0]['digest'] = 'sha256:' + release.sha(client.archive)
    elif problem == 'pypi_hash':
        client.pypi['urls'][0]['digests']['sha256'] = '0' * 64
    elif problem == 'pypi_files':
        client.pypi['urls'].pop()
    elif problem == 'pypi_yanked':
        client.pypi['urls'][0]['yanked'] = True
    elif problem == 'pypi_version':
        client.pypi['info']['version'] = '0.0.0'
    elif problem == 'public_bytes':
        client.files[next(iter(client.files))] = b'tampered'
    elif problem == 'changelog':
        client.source['CHANGELOG.rst'] = 'No section'
    elif problem == 'unstable_version':
        client.source['pyproject.toml'] = client.source['pyproject.toml'].replace('1.2.3', '1.2.3a1')
    elif problem == 'job_pagination':
        client.jobs['total_count'] = 101
    elif problem == 'artifact_pagination':
        client.artifacts['total_count'] = 101
    elif problem == 'tag_conflict':
        client.tag = 'b' * 40
    with pytest.raises(release.ReleaseError):
        release.publish(client, '123')
    assert not client.mutations


@pytest.mark.parametrize(
    'problem', ['body', 'name', 'prerelease', 'asset_digest', 'asset_size', 'extra_asset', 'missing_asset']
)
def test_conflicting_existing_release_is_never_overwritten(problem):
    client = Fake()
    release.publish(client, '123')
    client.mutations.clear()
    if problem in {'body', 'name'}:
        client.existing[problem] = 'Someone changed this'
    elif problem == 'prerelease':
        client.existing['prerelease'] = True
    elif problem == 'asset_digest':
        client.assets[0]['digest'] = 'sha256:' + '0' * 64
    elif problem == 'asset_size':
        client.assets[0]['size'] += 1
    elif problem == 'extra_asset':
        client.assets.append(dict(client.assets[0], name='other'))
    else:
        client.assets.pop()
    with pytest.raises(release.ReleaseError):
        release.publish(client, '123')
    assert not client.mutations


def test_artifact_redirect_drops_token():
    client = release.Client('synthetic-secret')
    calls = []

    class Response(io.BytesIO):
        pass

    def open_request(request, timeout):
        calls.append(request)
        if len(calls) == 1:
            raise urllib.error.HTTPError(
                request.full_url, 302, 'redirect', {'Location': 'https://storage.blob.core.windows.net/artifact'}, None
            )
        return Response(b'archive')

    client.opener.open = open_request
    assert client.api('/actions/artifacts/7/zip', raw=True) == b'archive'
    assert calls[0].get_header('Authorization') == 'Bearer synthetic-secret'
    assert not calls[1].has_header('Authorization')


@pytest.mark.parametrize('url', ['http://files.pythonhosted.org/file', 'https://example.invalid/file'])
def test_public_url_allowlist(url):
    with pytest.raises(release.ReleaseError, match='Unexpected PyPI host'):
        release.Client('synthetic').public(url)


def test_tls_error_is_not_bypassed_or_leaked():
    client = release.Client('synthetic-secret')

    def fail(*args, **kwargs):
        raise urllib.error.URLError('certificate failed sensitive-url')

    client.opener.open = fail
    with pytest.raises(release.ReleaseError, match='Network/TLS') as error:
        client.api('/actions/runs/123')
    assert 'sensitive-url' not in str(error.value)


def test_workflow_is_post_publication_and_has_job_scoped_permissions():
    text = (Path(__file__).parents[1] / '.github/workflows/github-release.yml').read_text()
    assert 'workflows: [Publish release]' in text and 'types: [completed]' in text
    assert 'permissions: {}' in text and '      actions: read\n      contents: write' in text
    assert 'id-token:' not in text and 'pull_request' not in text
    assert 'ref: main' in text and 'persist-credentials: false' in text
