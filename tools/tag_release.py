"""Create an idempotent GitHub release only for a verified PyPI publication.

Runs from trusted main, never executes downloaded source/artifacts. All writes are
additive except publishing our matching draft; conflicting state is never replaced.
"""

import argparse
import base64
import hashlib
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

import tomllib

REPO = 'matusowskymichael/pytest-Jira-xray-plus'
LIMIT = 50 * 1024 * 1024


class ReleaseError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ReleaseError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Client:
    def __init__(self, token):
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect)

    def request(self, url, method='GET', body=None, token=False, missing=False, raw=False):
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'verified-xray-release'}
        if token:
            headers['Authorization'] = 'Bearer ' + self.token
            headers['X-GitHub-Api-Version'] = '2026-03-10'
        if body is not None:
            headers['Content-Type'] = 'application/octet-stream' if raw else 'application/json'
            if not raw:
                body = json.dumps(body).encode()
        try:
            with self.opener.open(
                urllib.request.Request(url, data=body, headers=headers, method=method), timeout=60
            ) as r:
                data = r.read(LIMIT + 1)
        except urllib.error.HTTPError as exc:
            if missing and exc.code == 404:
                return None
            if method == 'GET' and exc.code == 302 and token:
                location = exc.headers['Location']
                host = urllib.parse.urlsplit(location)
                require(
                    host.scheme == 'https'
                    and host.hostname
                    and (
                        host.hostname.endswith('.blob.core.windows.net')
                        or host.hostname.endswith('.githubusercontent.com')
                    ),
                    'Unexpected artifact download host',
                )
                # Never forward the GitHub token to the signed storage URL.
                return self.request(location, raw=True)
            raise ReleaseError(f'HTTP {exc.code}; no credentials or response body logged') from None
        except (urllib.error.URLError, TimeoutError):
            raise ReleaseError('Network/TLS request failed; no bypass or credentials logged') from None
        require(len(data) <= LIMIT, 'Response exceeds size limit')
        return data if raw else json.loads(data)

    def api(self, path, method='GET', body=None, missing=False, raw=False):
        return self.request('https://api.github.com/repos/' + REPO + path, method, body, True, missing, raw)

    def public(self, url):
        parts = urllib.parse.urlsplit(url)
        require(
            parts.scheme == 'https' and parts.hostname in {'pypi.org', 'files.pythonhosted.org'}, 'Unexpected PyPI host'
        )
        return self.request(url, raw=True)

    def upload(self, release_id, name, data):
        path = f'https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={urllib.parse.quote(name)}'
        return json.loads(self.request(path, 'POST', data, token=True, raw=True))


def source(client, path, commit):
    data = client.api(f'/contents/{path}?ref={commit}')
    require(data['encoding'] == 'base64', 'Unexpected source encoding')
    return base64.b64decode(data['content']).decode()


def notes(changelog, version):
    match = re.search(rf'(?m)^{re.escape(version)} \[\d{{4}}-\d{{2}}-\d{{2}}\]\n=+\n', changelog)
    require(match, 'Version changelog section missing')
    rest = changelog[match.end() :]
    end = re.search(r'(?m)^\S[^\n]*\n=+\n', rest)
    result = rest[: end.start() if end else len(rest)].strip()
    require(result, 'Version changelog section empty')
    return result


def resolve_tag(client, tag):
    ref = client.api('/git/ref/tags/' + tag, missing=True)
    if ref is None:
        return None
    obj = ref['object']
    for _ in range(8):
        if obj['type'] == 'commit':
            return obj['sha']
        require(obj['type'] == 'tag' and re.fullmatch('[a-f0-9]{40}', obj['sha']), 'Invalid tag object')
        obj = client.api('/git/tags/' + obj['sha'])['object']
    raise ReleaseError('Tag chain too deep')


def find_release(client, tag):
    # The by-tag endpoint documents published releases; list also finds our draft
    # after an interrupted upload. Bound pagination rather than guess on truncation.
    matches = []
    for page in range(1, 11):
        releases = client.api(f'/releases?per_page=100&page={page}')
        matches.extend(r for r in releases if r['tag_name'] == tag)
        if len(releases) < 100:
            require(len(matches) <= 1, 'Ambiguous existing release')
            return matches[0] if matches else None
    raise ReleaseError('Release pagination limit reached')


def publish(client, run_id):
    require(re.fullmatch('[1-9][0-9]*', str(run_id)), 'Expected numeric publish run ID')
    run = client.api(f'/actions/runs/{run_id}')
    require(
        run['path'] == '.github/workflows/publish.yml'
        and run['event'] == 'workflow_dispatch'
        and run['head_branch'] == 'main'
        and run['head_repository']['full_name'] == REPO,
        'Run is not the trusted main publisher',
    )
    require(run['status'] == 'completed' and run['conclusion'] == 'success', 'Publisher run did not succeed')
    commit = run['head_sha']
    require(re.fullmatch('[a-f0-9]{40}', commit), 'Invalid publisher commit')
    jobs = client.api(f'/actions/runs/{run_id}/jobs?filter=latest&per_page=100')
    require(jobs['total_count'] == len(jobs['jobs']), 'Unexpected job pagination')
    states = {job['name']: job['conclusion'] for job in jobs['jobs']}
    if states.get('publish') == 'skipped':
        return {'status': 'skipped', 'reason': 'Dry run: PyPI publication was not requested'}
    require(states.get('build') == states.get('publish') == 'success', 'Build/publication job did not succeed')
    metadata = tomllib.loads(source(client, 'pyproject.toml', commit))['project']
    version = metadata['version']
    require(
        metadata['name'] == 'pytest-jira-xray-plus' and re.fullmatch(r'\d+\.\d+\.\d+', version),
        'Expected this package and a stable version',
    )
    changes = notes(source(client, 'CHANGELOG.rst', commit), version)
    artifacts = client.api(f'/actions/runs/{run_id}/artifacts?per_page=100')
    require(artifacts['total_count'] == len(artifacts['artifacts']), 'Unexpected artifact pagination')
    candidates = [a for a in artifacts['artifacts'] if a['name'] == 'verified-distributions']
    require(len(candidates) == 1 and not candidates[0]['expired'], 'Missing, ambiguous or expired publish artifact')
    artifact = candidates[0]
    archive = client.api(f'/actions/artifacts/{artifact["id"]}/zip', raw=True)
    require(artifact.get('digest') == 'sha256:' + sha(archive), 'Artifact archive hash mismatch')
    names = {f'pytest_jira_xray_plus-{version}-py3-none-any.whl', f'pytest_jira_xray_plus-{version}.tar.gz'}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        require(len(z.infolist()) == 2 and set(z.namelist()) == names, 'Unexpected distribution set')
        require(sum(f.file_size for f in z.infolist()) <= LIMIT, 'Expanded artifact exceeds size limit')
        files = {name: z.read(name) for name in names}
    pypi = json.loads(client.public(f'https://pypi.org/pypi/pytest-jira-xray-plus/{version}/json'))
    require(pypi['info']['version'] == version, 'PyPI version mismatch')
    require(len(pypi['urls']) == 2 and {f['filename'] for f in pypi['urls']} == names, 'PyPI file set mismatch')
    for item in pypi['urls']:
        require(not item['yanked'], 'PyPI release is yanked')
        name = item['filename']
        require(sha(files[name]) == item['digests']['sha256'], 'PyPI metadata/artifact hash mismatch')
        require(sha(client.public(item['url'])) == sha(files[name]), 'Public file/artifact hash mismatch')
    tag = 'v' + version
    body = (
        changes + f'\n\nPublished commit: `{commit}`\n\n'
        f'[Verified PyPI publication](https://github.com/{REPO}/actions/runs/{run_id}) · '
        f'[PyPI {version}](https://pypi.org/project/pytest-jira-xray-plus/{version}/)\n\n'
        'SHA-256 (assets are the exact published PyPI distributions):\n\n'
        + '\n'.join(f'- `{name}`: `{sha(files[name])}`' for name in sorted(files))
    )
    existing_tag = resolve_tag(client, tag)
    require(existing_tag in {None, commit}, 'Existing tag targets another commit; never overwrite')
    release = find_release(client, tag)
    if release:
        require(
            existing_tag == commit
            and release['name'] == tag
            and release['body'] == body
            and release['prerelease'] is False,
            'Existing release conflicts; never overwrite',
        )
    else:
        if existing_tag is None:
            client.api('/git/refs', 'POST', {'ref': 'refs/tags/' + tag, 'sha': commit})
        require(resolve_tag(client, tag) == commit, 'Tag changed before release creation')
        release = client.api(
            '/releases',
            'POST',
            {
                'tag_name': tag,
                'target_commitish': commit,
                'name': tag,
                'body': body,
                'draft': True,
                'prerelease': False,
            },
        )
    assets = client.api(f'/releases/{release["id"]}/assets?per_page=100')
    require(len(assets) <= 2 and len({a['name'] for a in assets}) == len(assets), 'Unexpected release assets')
    for asset in assets:
        require(
            asset['name'] in files
            and asset['state'] == 'uploaded'
            and asset.get('digest') == 'sha256:' + sha(files[asset['name']])
            and asset['size'] == len(files[asset['name']]),
            'Existing asset conflicts; never overwrite',
        )
    for name in sorted(files):
        if name not in {a['name'] for a in assets}:
            require(release['draft'], 'Published release missing an asset; manual review required')
            asset = client.upload(release['id'], name, files[name])
            require(asset.get('digest') == 'sha256:' + sha(files[name]), 'Uploaded asset hash mismatch')
    require(resolve_tag(client, tag) == commit, 'Tag changed before publication')
    release = client.api(f'/releases/{release["id"]}')
    require(
        release['body'] == body and release['name'] == tag and release['prerelease'] is False,
        'Release changed before publication',
    )
    final_assets = client.api(f'/releases/{release["id"]}/assets?per_page=100')
    require(len(final_assets) == 2 and {a['name'] for a in final_assets} == names, 'Final asset set mismatch')
    for asset in final_assets:
        require(
            asset['state'] == 'uploaded'
            and asset['size'] == len(files[asset['name']])
            and asset.get('digest') == 'sha256:' + sha(files[asset['name']]),
            'Final asset verification failed',
        )
    if release['draft']:
        client.api(f'/releases/{release["id"]}', 'PATCH', {'draft': False, 'make_latest': 'legacy'})
    return {'status': 'published', 'tag': tag, 'commit': commit, 'url': f'https://github.com/{REPO}/releases/tag/{tag}'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    try:
        require(bool(os.environ.get('GITHUB_TOKEN')), 'GITHUB_TOKEN is required')
        print(json.dumps(publish(Client(os.environ['GITHUB_TOKEN']), args.run_id)))
    except (ReleaseError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as exc:
        print(f'Release stopped: {exc if isinstance(exc, ReleaseError) else type(exc).__name__}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
