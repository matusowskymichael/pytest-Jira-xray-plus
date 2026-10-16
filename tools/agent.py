"""Repository checks and durable handoffs; no agent runtime or publishing commands."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ('harness', 'tests', 'offline', 'package', 'docs', 'lint-baseline', 'type-baseline')
STATES = {'not_started', 'in_progress', 'blocked', 'review_pending', 'passing', 'regression'}
ACTIVE = {'in_progress', 'review_pending', 'regression'}
COMMON = ('AGENTS.md', 'tools/agent.py', 'docs/agent', 'pyproject.toml', '.github/workflows')
PACKAGE_FILES = ('pyproject.toml', 'MANIFEST.in', 'LICENSE', 'NOTICE', 'README.md', 'README.rst', 'CHANGELOG.rst')
PACKAGE_DIRS = ('src', 'docs', 'tests', 'tools', 'examples')
BUILD_IGNORES = ('__pycache__', '*.pyc', '*.egg-info', '.pytest_cache')
EXCLUDED = ('feature_list.json', 'PROGRESS.md', 'docs/agent/evidence', '.harness')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def under(path, prefix):
    return path == prefix or path.startswith(prefix + '/')


def safe_path(root, value):
    require(isinstance(value, str) and value and not Path(value).is_absolute(), 'expected repository-relative path')
    require('..' not in Path(value).parts, 'parent traversal is forbidden')
    candidate = root / value
    require(candidate.resolve().is_relative_to(root.resolve()), f'path escapes repository: {value}')
    for part in (candidate, *candidate.parents):
        if part == root:
            break
        require(not part.is_symlink(), f'symlink is not allowed: {value}')
    return candidate


def stamp():
    return datetime.now(timezone.utc).isoformat()


def timestamp(value):
    parsed = datetime.fromisoformat(value)
    require(parsed.tzinfo is not None, 'timestamp must include timezone')
    require(parsed <= datetime.now(timezone.utc), 'future evidence timestamp')
    return parsed


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contract(task):
    return {
        key: task[key]
        for key in (
            'id',
            'title',
            'source',
            'scope',
            'prerequisites',
            'acceptance',
            'checks',
            'preserve',
            'implementer',
            'owner',
            'source_sha256',
            'source_url',
        )
    }


def fingerprint(root, task):
    paths = (
        subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root)
        .decode()
        .split('\0')
    )
    prefixes = (*COMMON, *task['scope'])
    if 'package' in task['checks']:
        prefixes += (*PACKAGE_FILES, *PACKAGE_DIRS)
        paths.extend((*PACKAGE_FILES, *PACKAGE_DIRS))
        # build_release copies the filesystem, including Git-ignored build inputs.
        for directory in PACKAGE_DIRS:
            base = safe_path(root, directory)
            paths.extend(
                path.relative_to(root).as_posix() for path in base.rglob('*') if path.is_file() or path.is_symlink()
            )
        paths = [
            p
            for p in paths
            if not any(fnmatch.fnmatch(part, pattern) for part in Path(p).parts for pattern in BUILD_IGNORES)
        ]
    selected = sorted(
        {p for p in paths if p and any(under(p, x) for x in prefixes) and not any(under(p, x) for x in EXCLUDED)}
    )
    payload = {'contract': contract(task), 'files': {}}
    for name in selected:
        path = safe_path(root, name)
        payload['files'][name] = file_hash(path) if path.is_file() else ('DIRECTORY' if path.is_dir() else 'MISSING')
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def validate_schema(root, data):
    require(isinstance(data, dict) and data.get('schema_version') == 1, 'unsupported ledger schema')
    tasks = data.get('tasks')
    require(isinstance(tasks, list) and tasks, 'ledger must contain tasks')
    require(all(isinstance(t, dict) for t in tasks), 'tasks must be objects')
    ids = [t.get('id') for t in tasks]
    require(all(isinstance(x, str) and re.fullmatch(r'XRAY-[A-Z]+-\d{3}', x) for x in ids), 'invalid task ID')
    require(len(set(ids)) == len(ids), 'duplicate task IDs')
    require(sum(t.get('state') in ACTIVE for t in tasks) <= 1, 'only one task may be active')
    for task in tasks:
        require(
            set(task)
            == {
                'id',
                'title',
                'source',
                'scope',
                'prerequisites',
                'acceptance',
                'checks',
                'preserve',
                'implementer',
                'state',
                'evidence',
                'review',
                'blocker',
                'owner',
                'next_action',
                'source_sha256',
                'source_url',
            },
            f'invalid fields: {task["id"]}',
        )
        for field in ('title', 'implementer', 'owner', 'next_action'):
            require(isinstance(task[field], str) and task[field].strip(), f'missing {field}')
        require(safe_path(root, task['source']).is_file(), 'missing task source')
        require(
            task['source_sha256'] == hashlib.sha256(safe_path(root, task['source']).read_bytes().strip()).hexdigest(),
            'local scope drift: review and reconcile the task source',
        )
        require(
            task['source_url'] is None
            or re.fullmatch(
                r'https://github.com/matusowskymichael/pytest-Jira-xray-plus/(issues|pull)/[0-9]+', task['source_url']
            ),
            'invalid scope source URL',
        )
        require(task['state'] in STATES, 'invalid task state')
        for field in ('scope', 'prerequisites', 'acceptance', 'checks', 'evidence'):
            values = task[field]
            require(
                isinstance(values, list) and all(isinstance(v, str) and v.strip() for v in values), f'invalid {field}'
            )
            require(len(values) == len(set(values)), f'duplicate {field}')
        require(task['scope'] and task['acceptance'] and task['checks'], 'scope, acceptance and checks cannot be empty')
        require('harness' in task['checks'] and set(task['checks']) <= set(PROFILES), 'unknown/missing checks')
        require(all(x in ids and x != task['id'] for x in task['prerequisites']), 'unknown/self prerequisite')
        for name in task['scope']:
            safe_path(root, name)
        require(isinstance(task['preserve'], dict), 'invalid preservation map')
        for name, digest in task['preserve'].items():
            safe_path(root, name)
            require(isinstance(digest, str) and re.fullmatch(r'[a-f0-9]{64}', digest), 'invalid preserved hash')
        require(task['review'] is None or isinstance(task['review'], str), 'invalid review reference')
        require(isinstance(task['blocker'], str), 'invalid blocker')
        require(task['state'] != 'blocked' or task['blocker'].strip(), 'blocked task needs an actionable reason')
    by_id = {t['id']: t for t in tasks}
    visiting, visited = set(), set()

    def visit(key):
        require(key not in visiting, 'cyclic prerequisites')
        if key in visited:
            return
        visiting.add(key)
        for dependency in by_id[key]['prerequisites']:
            visit(dependency)
        visiting.remove(key)
        visited.add(key)

    for key in ids:
        visit(key)
    return by_id


def commands(root, profile):
    py = sys.executable
    if profile == 'harness':
        return [[py, 'tools/check_harness_tests.py']]
    if profile == 'tests':
        return [[py, '-m', 'pytest', '-q']]
    if profile == 'offline':
        return [[py, 'tools/reproduce.py', 'src', '--details'], [py, 'tools/validate_offline.py']]
    if profile == 'docs':
        return [
            [py, 'tools/prepare_docs_site.py'],
            [py, '-m', 'mkdocs', 'build', '--strict'],
            [py, 'tools/check_docs_links.py'],
            [py, 'tools/check_docs_browser.py'],
        ]
    if profile == 'lint-baseline':
        return [[py, '-m', 'ruff', 'check', '--no-cache', 'src', 'tests', 'tools']]
    if profile == 'type-baseline':
        return [[py, '-m', 'mypy', '--cache-dir', str(root / '.harness/mypy-cache'), 'src', 'tests']]
    require(profile == 'package', 'unknown profile')
    import tomllib

    version = tomllib.loads((root / 'pyproject.toml').read_text())['project']['version']
    require(re.fullmatch(r'[0-9a-zA-Z.]+', version), 'invalid package version')
    dist = '.harness/dist'
    wheel = f'{dist}/pytest_jira_xray_plus-{version}-py3-none-any.whl'
    sdist = f'{dist}/pytest_jira_xray_plus-{version}.tar.gz'
    installed = str(root / '.harness/installed' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'))
    return [
        [py, 'tools/build_release.py', dist],
        [py, '-m', 'twine', 'check', wheel, sdist],
        [py, '-m', 'venv', '--clear', '.harness/installed'],
        [installed, '-m', 'pip', 'install', wheel, 'pytest-xdist==3.8.0', 'pytest-rerunfailures==16.7'],
        [py, 'tools/check_installed_usage.py', installed, wheel],
    ]


def command_contract(root, profile):
    return [
        [arg.replace(sys.executable, '{python}').replace(str(root), '{root}') for arg in argv]
        for argv in commands(root, profile)
    ]


def require_revision(root, revision):
    require(isinstance(revision, str) and re.fullmatch(r'[a-f0-9]{40}', revision), 'invalid evidence revision')
    result = subprocess.run(
        ['git', 'cat-file', '-e', revision + '^{commit}'],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode:
        shallow = git(root, 'rev-parse', '--is-shallow-repository') == 'true'
        remedy = 'run git fetch --unshallow, then retry' if shallow else 'fetch the recorded history, then retry'
        raise ValueError(f'evidence revision unavailable: {revision}; {remedy}')


def validate_receipt(root, task, name):
    path = safe_path(root, name)
    require(under(name, 'docs/agent/evidence'), 'accepted evidence must be versioned under docs/agent/evidence')
    receipt = read(path)
    require(receipt['task'] == task['id'] and receipt['digest'] == fingerprint(root, task), 'stale/wrong-task evidence')
    require(receipt['status'] == 'passed' and receipt['profile'] in task['checks'], 'failed/unknown check evidence')
    require(re.fullmatch(r'[a-f0-9]{40}', receipt['revision']), 'invalid tested revision')
    timestamp(receipt['timestamp'])
    require_revision(root, receipt['revision'])
    expected = command_contract(root, receipt['profile'])
    require(receipt['commands'] == expected, 'verification commands changed')
    require(len(receipt['results']) == len(expected), 'missing command results')
    for result in receipt['results']:
        require(type(result['exit_code']) is int and result['exit_code'] == 0, 'nonzero/missing result')
        log = safe_path(root, result['log'])
        require(log.is_file() and file_hash(log) == result['log_sha256'], 'missing/modified check log')
    return receipt


def validate_acceptance(root, task, evidence, review_name):
    receipts = [validate_receipt(root, task, name) for name in evidence]
    require({r['profile'] for r in receipts} == set(task['checks']), 'missing required checks')
    require(len(receipts) == len(task['checks']), 'duplicate profile receipts')
    require(
        isinstance(review_name, str) and under(review_name, 'docs/agent/evidence'),
        'missing versioned independent review',
    )
    review = read(safe_path(root, review_name))
    require(re.fullmatch(r'[a-f0-9]{40}', review['revision']), 'invalid reviewed revision')
    require_revision(root, review['revision'])
    require(review['task'] == task['id'] and review['digest'] == fingerprint(root, task), 'stale/wrong-task review')
    require(
        review['independent'] is True
        and isinstance(review['reviewer'], str)
        and review['reviewer'].strip()
        and review['reviewer'] != task['implementer'],
        'independent reviewer required',
    )
    require(review['verdict'] == 'pass' and review['findings'] == [], 'unresolved review findings')
    require(set(review['acceptance']) == set(task['acceptance']), 'review must cover every acceptance criterion')
    require(
        timestamp(review['timestamp']) >= max(timestamp(r['timestamp']) for r in receipts),
        'review predates verification',
    )


def validate(root, data):
    tasks = validate_schema(root, data)
    for task in tasks.values():
        for name, digest in task['preserve'].items():
            path = safe_path(root, name)
            require(path.is_file() and file_hash(path) == digest, f'protected baseline changed: {name}')
        if task['state'] in ACTIVE | {'passing'}:
            require(all(tasks[x]['state'] == 'passing' for x in task['prerequisites']), 'prerequisites are not passing')
        if task['state'] == 'passing':
            validate_acceptance(root, task, task['evidence'], task['review'])
    # Check local documentation routes without requiring third-party Markdown tools.
    for path in [root / 'AGENTS.md', root / 'PROGRESS.md', *sorted((root / 'docs/agent').glob('*.md'))]:
        require(path.is_file(), f'missing documentation: {path.name}')
        for link in re.findall(r'\]\(([^\s)]+)\)', path.read_text()):
            if '://' in link or link.startswith('#'):
                continue
            target = (path.parent / link.split('#')[0]).resolve()
            require(
                target.is_relative_to(root.resolve()) and target.exists(), f'broken local documentation link: {link}'
            )
    return tasks


def reopen(root, tasks, selected, reason):
    """Invalidate stale proofs and dependents together; never manufacture acceptance."""
    affected = {selected['id']}
    for task in tasks.values():
        if task['state'] == 'passing':
            try:
                validate_acceptance(root, task, task['evidence'], task['review'])
            except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
                affected.add(task['id'])
    while True:
        dependents = {task['id'] for task in tasks.values() if set(task['prerequisites']) & affected}
        expanded = affected | dependents
        if expanded == affected:
            break
        affected = expanded
    for key in sorted(affected):
        task = tasks[key]
        task.update(
            state='blocked',
            blocker=f'Reopened {selected["id"]}: {reason}; reverify prerequisites and evidence',
            next_action=f'python tools/agent.py reopen --task {key} --summary "ready for revalidation"',
        )
    if all(tasks[key]['state'] == 'passing' for key in selected['prerequisites']) and not any(
        task['state'] in ACTIVE for task in tasks.values()
    ):
        selected['state'] = 'regression'
    # Caller performs complete validation before one atomic ledger write.


def select(tasks, task_id):
    if task_id:
        require(task_id in tasks, 'unknown task')
        return tasks[task_id]
    active = [t for t in tasks.values() if t['state'] in ACTIVE]
    if not active and len(tasks) == 1:
        return next(iter(tasks.values()))
    require(len(active) == 1, 'select a task with --task')
    return active[0]


def check(root, task, profile, record_dir):
    require(
        profile in task['checks'] or profile in ('lint-baseline', 'type-baseline'), 'profile not required by this task'
    )
    require(record_dir in ('.harness/evidence', 'docs/agent/evidence'), 'unsupported evidence directory')
    safe_path(root, '.harness/installed')
    safe_path(root, '.harness/dist')
    out = safe_path(root, record_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_id = f'{task["id"]}-{profile}-{uuid4().hex[:12]}'
    digest = fingerprint(root, task)
    receipt = {
        'task': task['id'],
        'profile': profile,
        'digest': digest,
        'revision': git(root, 'rev-parse', 'HEAD'),
        'timestamp': stamp(),
        'commands': command_contract(root, profile),
        'results': [],
        'status': 'not_run',
    }
    secrets = [
        v
        for k, v in os.environ.items()
        if len(v) >= 6 and any(word in k.upper() for word in ('TOKEN', 'PASSWORD', 'SECRET', 'API_KEY'))
    ]
    env = {k: v for k, v in os.environ.items() if not k.startswith(('XRAY_', 'PYTEST', 'PYTHONPATH'))}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    for index, argv in enumerate(commands(root, profile)):
        started = time.monotonic()
        try:
            result = subprocess.run(
                argv, cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300
            )
            output, code = result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            output, code = 'Check timed out after 300 seconds; partial output omitted.\n', 124
        except KeyboardInterrupt:
            output, code = 'Check interrupted; rerun before acceptance.\n', 130
        except OSError as exc:
            output, code = f'Unable to execute check: {type(exc).__name__}\n', 127
        for secret in secrets:
            output = output.replace(secret, '[REDACTED]')
        log = out / f'{run_id}-{index}.log'
        log.write_text(output, encoding='utf-8')
        receipt['results'].append(
            {
                'exit_code': code,
                'duration_seconds': round(time.monotonic() - started, 3),
                'log': log.relative_to(root).as_posix(),
                'log_sha256': file_hash(log),
            }
        )
        receipt['status'] = (
            'passed' if code == 0 else ('interrupted' if code == 130 else ('blocked' if code == 127 else 'failed'))
        )
        if code:
            break
    if fingerprint(root, task) != digest:
        receipt['status'] = 'stale'
    receipt['timestamp'] = stamp()
    target = out / f'{run_id}.json'
    write(target, receipt)
    print(
        json.dumps({'profile': profile, 'status': receipt['status'], 'evidence': target.relative_to(root).as_posix()})
    )
    return 0 if receipt['status'] == 'passed' else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'action', choices=['preflight', 'resume', 'drift', 'check', 'checkpoint', 'start', 'block', 'reopen', 'accept']
    )
    parser.add_argument('--task')
    parser.add_argument('--profile', choices=PROFILES, default='harness')
    parser.add_argument('--record-dir', default='.harness/evidence')
    parser.add_argument('--summary')
    parser.add_argument('--next', dest='next_action')
    parser.add_argument('--review')
    parser.add_argument('--remote', action='store_true', help='Read current GitHub scope when running drift')
    parser.add_argument('--evidence', nargs='*', default=[])
    args = parser.parse_args(argv)
    root = ROOT
    try:
        require(sys.version_info >= (3, 12), 'Python 3.12+ required')
        require(Path(git(root, 'rev-parse', '--show-toplevel')).resolve() == root.resolve(), 'unexpected checkout root')
        data = read(root / 'feature_list.json')
        # Explicit reopen is the recovery path for stale passing evidence.
        tasks = validate_schema(root, data) if args.action == 'reopen' else validate(root, data)
        task = select(tasks, args.task)
        digest = fingerprint(root, task)
        if args.action == 'check':
            return check(root, task, args.profile, args.record_dir)
        if args.action in ('preflight', 'drift'):
            if args.remote:
                require(args.action == 'drift' and task['source_url'], 'remote scope not configured; not checked')
                kind, number = task['source_url'].split('/')[-2:]
                endpoint = 'pulls' if kind == 'pull' else 'issues'
                response = subprocess.check_output(
                    ['gh', 'api', f'repos/matusowskymichael/pytest-Jira-xray-plus/{endpoint}/{number}'],
                    cwd=root,
                    text=True,
                )
                body = json.loads(response)['body']
                require(
                    hashlib.sha256(body.strip().encode()).hexdigest() == task['source_sha256'],
                    'remote scope drift: reconcile reviewed GitHub body explicitly',
                )
            print(
                json.dumps(
                    {
                        'status': 'passed',
                        'root': str(root),
                        'revision': git(root, 'rev-parse', 'HEAD'),
                        'branch': git(root, 'branch', '--show-current'),
                        'changes': git(root, 'status', '--short'),
                        'task': task['id'],
                        'state': task['state'],
                        'digest': digest,
                        'limits': (
                            'Structure/baseline only; does not run tests or prove live Jira compatibility. '
                            'Remote scope is checked only with --remote.'
                        ),
                    },
                    indent=2,
                )
            )
        elif args.action == 'checkpoint':
            require(args.summary and args.next_action, 'checkpoint needs --summary and --next')
            target = safe_path(root, '.harness/checkpoint.json')
            write(
                target,
                {
                    'root': str(root),
                    'task': task['id'],
                    'revision': git(root, 'rev-parse', 'HEAD'),
                    'digest': digest,
                    'timestamp': stamp(),
                    'summary': args.summary,
                    'next': args.next_action,
                },
            )
            print('Checkpoint saved; task acceptance unchanged. Update PROGRESS.md before handoff.')
        elif args.action == 'resume':
            print((root / 'PROGRESS.md').read_text())
            target = safe_path(root, '.harness/checkpoint.json')
            if not target.exists():
                print('No local checkpoint: use versioned progress, inspect the checkout, then checkpoint.')
            else:
                saved = read(target)
                require(
                    saved['root'] == str(root) and saved['task'] == task['id'] and saved['digest'] == digest,
                    'stale/different-checkout checkpoint; inspect changes and create a new checkpoint',
                )
                print(json.dumps(saved, indent=2))
        else:
            if args.action == 'start':
                require(
                    not any(t['id'] != task['id'] and t['state'] in ACTIVE for t in tasks.values()),
                    'another task is active',
                )
                require(
                    task['state'] != 'passing' and all(tasks[x]['state'] == 'passing' for x in task['prerequisites']),
                    'task not eligible',
                )
                task['state'], task['blocker'] = 'in_progress', ''
            elif args.action in ('block', 'reopen'):
                require(args.summary, 'state change needs --summary')
                require(args.action != 'block' or task['state'] != 'passing', 'reopen passing work explicitly')
                if args.action == 'reopen':
                    reopen(root, tasks, task, args.summary)
                else:
                    task['state'], task['blocker'] = 'blocked', args.summary
            else:
                validate_acceptance(root, task, args.evidence, args.review)
                task.update(state='passing', evidence=args.evidence, review=args.review, blocker='')
            validate(root, data)
            write(root / 'feature_list.json', data)
            print(f'{task["id"]}: {task["state"]}')
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        print(f'Harness blocked: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
