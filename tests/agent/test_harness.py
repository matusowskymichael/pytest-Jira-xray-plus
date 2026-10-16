"""Synthetic lifecycle fixtures; review identities below are test data only."""

import ast
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import agent, check_harness_tests

REPOSITORY = Path(__file__).resolve().parents[2]


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ('AGENTS.md', 'PROGRESS.md', 'docs/agent/task.md', 'src/model.py'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('fixture\n')
        (self.root / '.gitignore').write_text('.harness/\n')
        for args in (
            ('init', '-q'),
            ('config', 'user.email', 'fixture@example.invalid'),
            ('config', 'user.name', 'Fixture'),
            ('add', '.'),
            ('commit', '-qm', 'fixture'),
        ):
            agent.git(self.root, *args)
        self.task = dict(
            id='XRAY-TEST-001',
            title='Fixture',
            source='docs/agent/task.md',
            source_sha256=hashlib.sha256(b'fixture').hexdigest(),
            source_url=None,
            owner='Fixture owner',
            implementer='fixture-builder',
            scope=['src'],
            prerequisites=[],
            acceptance=['fixture criterion'],
            checks=['harness'],
            preserve={},
            state='in_progress',
            evidence=[],
            review=None,
            blocker='',
            next_action='python tools/agent.py preflight',
        )
        self.data = dict(schema_version=1, tasks=[self.task])
        self.save()

    def save(self):
        agent.write(self.root / 'feature_list.json', self.data)

    def cli(self, *args):
        self.save()
        with patch.object(agent, 'ROOT', self.root), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return agent.main(list(args))

    def receipt(self, code=0, effect=None):
        command = [[sys.executable, '-c', f'print("fixture output"); raise SystemExit({code})']]
        with patch.object(agent, 'commands', return_value=command):
            if effect:
                original_run = subprocess.run

                def interrupt_check(argv, **kwargs):
                    if argv[0] == 'git':
                        return original_run(argv, **kwargs)
                    raise effect

                with patch.object(agent.subprocess, 'run', side_effect=interrupt_check):
                    result = agent.check(self.root, self.task, 'harness', 'docs/agent/evidence')
            else:
                result = agent.check(self.root, self.task, 'harness', 'docs/agent/evidence')
        path = next((self.root / 'docs/agent/evidence').glob('*.json'))
        return result, path.relative_to(self.root).as_posix(), command

    def review(self):
        name = 'docs/agent/evidence/review.json'
        agent.write(
            self.root / name,
            dict(
                task=self.task['id'],
                digest=agent.fingerprint(self.root, self.task),
                revision=agent.git(self.root, 'rev-parse', 'HEAD'),
                timestamp=agent.stamp(),
                independent=True,
                reviewer='independent-fixture',
                verdict='pass',
                findings=[],
                acceptance=self.task['acceptance'],
            ),
        )
        return name

    def accept_fixture(self, task):
        """Produce actual successful command receipts, with synthetic review data."""
        command = [[sys.executable, '-c', 'print("fixture check")']]
        with patch.object(agent, 'commands', return_value=command), redirect_stdout(io.StringIO()):
            self.assertEqual(agent.check(self.root, task, 'harness', 'docs/agent/evidence'), 0)
        name = next((self.root / 'docs/agent/evidence').glob(task['id'] + '-harness-*.json'))
        review_name = 'docs/agent/evidence/' + task['id'] + '-review.json'
        agent.write(
            self.root / review_name,
            dict(
                task=task['id'],
                digest=agent.fingerprint(self.root, task),
                revision=agent.git(self.root, 'rev-parse', 'HEAD'),
                timestamp=agent.stamp(),
                independent=True,
                reviewer='independent-fixture',
                verdict='pass',
                findings=[],
                acceptance=task['acceptance'],
            ),
        )
        task.update(state='passing', evidence=[name.relative_to(self.root).as_posix()], review=review_name)
        return command

    def test_accepted_history_in_fresh_shallow_clone(self):
        command = self.accept_fixture(self.task)
        self.save()
        agent.git(self.root, 'add', '.')
        agent.git(self.root, 'commit', '-qm', 'accepted evidence only')
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / 'clone'
            subprocess.run(['git', 'clone', '-q', '--depth=1', self.root.as_uri(), str(clone)], check=True)
            data = agent.read(clone / 'feature_list.json')
            with patch.object(agent, 'commands', return_value=command):
                with self.assertRaisesRegex(ValueError, 'fetch --unshallow'):
                    agent.validate(clone, data)
                agent.git(clone, 'fetch', '--unshallow')
                agent.validate(clone, data)
                self.assertEqual(agent.fingerprint(clone, data['tasks'][0]), agent.fingerprint(self.root, self.task))
        workflow = (REPOSITORY / '.github/workflows/agent.yml').read_text()
        self.assertIn('fetch-depth: 0', workflow)

    def test_reopen_shared_content_and_dependents_in_either_order(self):
        for dependent_state in ('passing', 'in_progress'):
            for first in ('XRAY-TEST-001', 'XRAY-TEST-002'):
                with self.subTest(dependent_state=dependent_state, first=first):
                    # All task proofs cover shared src; C is unrelated to the A -> B dependency.
                    tasks = [copy.deepcopy(self.task) for _ in range(3)]
                    for i, task in enumerate(tasks):
                        task.update(id=f'XRAY-TEST-{i + 1:03}', state='not_started', evidence=[], review=None)
                    tasks[1]['prerequisites'] = [tasks[0]['id']]
                    self.data['tasks'] = tasks
                    for task in tasks:
                        command = self.accept_fixture(task)
                    tasks[1]['state'] = dependent_state
                    with patch.object(agent, 'commands', return_value=command):
                        agent.validate(self.root, self.data)
                        (self.root / 'src/model.py').write_text(first + dependent_state)
                        self.assertEqual(self.cli('preflight', '--task', first), 1)
                        self.assertEqual(self.cli('reopen', '--task', first, '--summary', 'shared source changed'), 0)
                        self.data = agent.read(self.root / 'feature_list.json')
                        agent.validate(self.root, self.data)
                        current = {t['id']: t for t in self.data['tasks']}
                        self.assertEqual(current['XRAY-TEST-002']['state'], 'blocked')
                        self.assertEqual(current['XRAY-TEST-003']['state'], 'blocked')
                        self.assertNotEqual(current['XRAY-TEST-001']['state'], 'passing')
                        self.assertEqual(
                            self.cli('reopen', '--task', 'XRAY-TEST-001', '--summary', 'repair prerequisite'), 0
                        )
                        self.data = agent.read(self.root / 'feature_list.json')
                        self.assertEqual(self.data['tasks'][0]['state'], 'regression')
                        self.assertEqual(self.cli('start', '--task', 'XRAY-TEST-002'), 1)
                        # Old evidence cannot establish acceptance after invalidation.
                        with self.assertRaisesRegex(ValueError, 'stale'):
                            agent.validate_acceptance(self.root, tasks[0], tasks[0]['evidence'], tasks[0]['review'])
                    for path in (self.root / 'docs/agent/evidence').iterdir():
                        path.unlink()

    def test_reopen_failed_validation_does_not_write_partial_ledger(self):
        self.task['preserve'] = {'src/model.py': agent.file_hash(self.root / 'src/model.py')}
        self.save()
        before = (self.root / 'feature_list.json').read_bytes()
        (self.root / 'src/model.py').write_text('protected change')
        self.assertEqual(self.cli('reopen', '--summary', 'cannot bypass preservation'), 1)
        self.assertEqual(before, (self.root / 'feature_list.json').read_bytes())

    def test_package_inputs_mutation_and_deletion_change_digest(self):
        self.task['checks'].append('package')
        names = [
            'MANIFEST.in',
            'LICENSE',
            'NOTICE',
            'README.rst',
            'CHANGELOG.rst',
            'examples/extra.py',
            'tools/build_release.py',
            'docs/build-input.txt',
            'tests/fixture.txt',
            'src/model.py',
            'README.md',
            'pyproject.toml',
        ]
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('original')
        agent.git(self.root, 'add', '.')
        baseline = agent.fingerprint(self.root, self.task)
        for name in names:
            with self.subTest(name=name):
                path = self.root / name
                path.write_text('mutation')
                self.assertNotEqual(baseline, agent.fingerprint(self.root, self.task))
                path.unlink()
                self.assertNotEqual(baseline, agent.fingerprint(self.root, self.task))
                path.write_text('original')
        (self.root / '.gitignore').write_text('examples/ignored.txt\n')
        (self.root / 'examples/ignored.txt').write_text('copied by build_release despite gitignore')
        self.assertNotEqual(baseline, agent.fingerprint(self.root, self.task))

    def test_valid_schema_and_preflight(self):
        self.assertEqual(self.cli('preflight'), 0)

    def test_missing_required_fields(self):
        del self.task['owner']
        with self.assertRaises(ValueError):
            agent.validate_schema(self.root, self.data)

    def test_unknown_profile(self):
        self.task['checks'].append('pretend')
        with self.assertRaises(ValueError):
            agent.validate_schema(self.root, self.data)

    def test_missing_dependency(self):
        self.task['prerequisites'] = ['XRAY-NO-001']
        with self.assertRaises(ValueError):
            agent.validate_schema(self.root, self.data)

    def test_cycles(self):
        other = copy.deepcopy(self.task)
        other.update(id='XRAY-TEST-002', state='not_started', prerequisites=[self.task['id']])
        self.task['prerequisites'] = [other['id']]
        self.data['tasks'].append(other)
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            agent.validate_schema(self.root, self.data)

    def test_concurrent_tasks(self):
        other = copy.deepcopy(self.task)
        other['id'] = 'XRAY-TEST-002'
        self.data['tasks'].append(other)
        with self.assertRaisesRegex(ValueError, 'one task'):
            agent.validate_schema(self.root, self.data)

    def test_unfinished_prerequisite(self):
        other = copy.deepcopy(self.task)
        other.update(id='XRAY-TEST-002', state='not_started')
        self.task['prerequisites'] = [other['id']]
        self.data['tasks'].append(other)
        with self.assertRaisesRegex(ValueError, 'not passing'):
            agent.validate(self.root, self.data)

    def test_block_requires_reason(self):
        self.task['state'] = 'blocked'
        with self.assertRaises(ValueError):
            agent.validate_schema(self.root, self.data)
        self.task['blocker'] = 'Install test tools'
        agent.validate_schema(self.root, self.data)

    def test_scope_drift(self):
        (self.root / 'docs/agent/task.md').write_text('changed scope')
        self.assertEqual(self.cli('drift'), 1)

    def test_preserved_source(self):
        self.task['preserve'] = {'src/model.py': agent.file_hash(self.root / 'src/model.py')}
        (self.root / 'src/model.py').write_text('changed runtime')
        self.assertEqual(self.cli('preflight'), 1)

    def test_digest_excludes_progress_evidence_and_state(self):
        before = agent.fingerprint(self.root, self.task)
        self.task['state'] = 'blocked'
        self.task['blocker'] = 'fixture'
        self.save()
        (self.root / 'PROGRESS.md').write_text('handoff')
        agent.write(self.root / 'docs/agent/evidence/result.json', {})
        self.assertEqual(before, agent.fingerprint(self.root, self.task))
        (self.root / 'src/new.py').write_text('new untracked code')
        self.assertNotEqual(before, agent.fingerprint(self.root, self.task))

    def test_path_traversal_and_symlink(self):
        for path in ('../elsewhere', '/tmp/elsewhere'):
            with self.assertRaises(ValueError):
                agent.safe_path(self.root, path)
        (self.root / 'alias').symlink_to(self.root / 'src', target_is_directory=True)
        with self.assertRaises(ValueError):
            agent.safe_path(self.root, 'alias/model.py')

    def test_missing_receipt(self):
        with self.assertRaises(FileNotFoundError):
            agent.validate_receipt(self.root, self.task, 'docs/agent/evidence/missing.json')

    def test_failed_receipt(self):
        result, name, command = self.receipt(1)
        self.assertEqual(result, 1)
        with patch.object(agent, 'commands', return_value=command), self.assertRaises(ValueError):
            agent.validate_receipt(self.root, self.task, name)

    def test_stale_receipt(self):
        _, name, command = self.receipt()
        (self.root / 'src/model.py').write_text('different')
        with patch.object(agent, 'commands', return_value=command), self.assertRaisesRegex(ValueError, 'stale'):
            agent.validate_receipt(self.root, self.task, name)

    def test_modified_or_missing_log(self):
        _, name, command = self.receipt()
        log = self.root / agent.read(self.root / name)['results'][0]['log']
        with patch.object(agent, 'commands', return_value=command):
            log.write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'log'):
                agent.validate_receipt(self.root, self.task, name)
            log.unlink()
            with self.assertRaisesRegex(ValueError, 'log'):
                agent.validate_receipt(self.root, self.task, name)

    def test_changed_commands(self):
        _, name, _ = self.receipt()
        with self.assertRaisesRegex(ValueError, 'commands changed'):
            agent.validate_receipt(self.root, self.task, name)

    def test_missing_check_or_review(self):
        with self.assertRaisesRegex(ValueError, 'missing required'):
            agent.validate_acceptance(self.root, self.task, [], None)
        _, name, command = self.receipt()
        with patch.object(agent, 'commands', return_value=command), self.assertRaisesRegex(ValueError, 'review'):
            agent.validate_acceptance(self.root, self.task, [name], None)

    def test_builder_review_rejected(self):
        _, name, command = self.receipt()
        review_name = self.review()
        review = agent.read(self.root / review_name)
        review['reviewer'] = self.task['implementer']
        agent.write(self.root / review_name, review)
        with patch.object(agent, 'commands', return_value=command), self.assertRaisesRegex(ValueError, 'independent'):
            agent.validate_acceptance(self.root, self.task, [name], review_name)

    def test_acceptance_then_reopen_stale_state(self):
        _, name, command = self.receipt()
        review_name = self.review()
        with patch.object(agent, 'commands', return_value=command):
            self.assertEqual(self.cli('accept', '--review', review_name, '--evidence', name), 0)
            self.data = agent.read(self.root / 'feature_list.json')
            self.task = self.data['tasks'][0]
            self.assertEqual(self.task['state'], 'passing')
            # Evidence-only commits do not invalidate the content-bound review.
            agent.git(self.root, 'add', '.')
            agent.git(self.root, 'commit', '-qm', 'evidence')
            self.assertEqual(self.cli('preflight'), 0)
            (self.root / 'src/model.py').write_text('regression')
            self.assertEqual(self.cli('preflight'), 1)
            self.assertEqual(self.cli('reopen', '--summary', 'source changed; rerun checks'), 0)
            self.assertEqual(agent.read(self.root / 'feature_list.json')['tasks'][0]['state'], 'regression')

    def test_checkpoint_resume_and_stale_recovery(self):
        self.assertEqual(self.cli('resume'), 0)
        self.assertEqual(self.cli('checkpoint', '--summary', 'fixture done', '--next', 'run tests'), 0)
        self.assertEqual(self.cli('resume'), 0)
        (self.root / 'src/model.py').write_text('new work')
        self.assertEqual(self.cli('resume'), 1)
        self.assertEqual(self.cli('checkpoint', '--summary', 'inspected new work', '--next', 'run tests'), 0)
        self.assertEqual(self.cli('resume'), 0)

    def test_interruption_and_timeout_record_failure(self):
        for error, status in (
            (KeyboardInterrupt(), 'interrupted'),
            (subprocess.TimeoutExpired('fixture', 300), 'failed'),
            (FileNotFoundError(), 'blocked'),
        ):
            with self.subTest(status=status):
                result, name, _ = self.receipt(effect=error)
                self.assertEqual(result, 1)
                self.assertEqual(agent.read(self.root / name)['status'], status)
                for path in (self.root / 'docs/agent/evidence').iterdir():
                    path.unlink()

    def test_environment_and_output_redaction(self):
        command = [
            [sys.executable, '-c', 'import os; print(os.getenv("XRAY_TOKEN", "scrubbed")); print("synthetic-secret")']
        ]
        with (
            patch.dict('os.environ', {'XRAY_TOKEN': 'synthetic-secret'}),
            patch.object(agent, 'commands', return_value=command),
        ):
            agent.check(self.root, self.task, 'harness', 'docs/agent/evidence')
        output = next((self.root / 'docs/agent/evidence').glob('*.log')).read_text()
        self.assertEqual(output, 'scrubbed\n[REDACTED]\n')

    def test_remote_scope_unconfigured_fails(self):
        self.assertEqual(self.cli('drift', '--remote'), 1)

    def test_empty_suite_fails(self):
        empty = self.root / 'empty'
        empty.mkdir()
        with redirect_stderr(io.StringIO()):
            self.assertEqual(check_harness_tests.run(empty), 1)

    def test_all_skipped_suite_fails(self):
        suite = unittest.TestSuite()
        case = unittest.FunctionTestCase(lambda: None)
        case.setUp = lambda: self.skipTest('synthetic unavailable check')
        suite.addTest(case)
        with patch.object(unittest.TestLoader, 'discover', return_value=suite), redirect_stderr(io.StringIO()):
            self.assertEqual(check_harness_tests.run(self.root), 1)

    def test_remote_scope_changed_or_unavailable(self):
        self.task['source_url'] = 'https://github.com/matusowskymichael/pytest-Jira-xray-plus/pull/999'
        original = subprocess.check_output

        def remote(argv, **kwargs):
            if argv[0] == 'gh':
                return json.dumps({'body': 'changed scope'})
            return original(argv, **kwargs)

        with patch.object(agent.subprocess, 'check_output', side_effect=remote):
            self.assertEqual(self.cli('drift', '--remote'), 1)

        def unavailable(argv, **kwargs):
            if argv[0] == 'gh':
                raise FileNotFoundError('gh unavailable')
            return original(argv, **kwargs)

        with patch.object(agent.subprocess, 'check_output', side_effect=unavailable):
            self.assertEqual(self.cli('drift', '--remote'), 1)

    def test_pure_case_model_import_boundary(self):
        tree = ast.parse((REPOSITORY / 'src/pytest_xray/case_results.py').read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or '').split('.')[0])
        self.assertLessEqual(imports, sys.stdlib_module_names)


if __name__ == '__main__':
    unittest.main()
