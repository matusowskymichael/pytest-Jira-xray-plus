"""Measure plugin coverage, including Python subprocesses; never deploy a report."""

import argparse
import datetime
import hashlib
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / '.coveragerc'


def source_digest(root):
    files = sorted((root / 'src/pytest_xray').rglob('*.py'))
    records = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def summarize(data, root, provenance):
    expected = {p.relative_to(root).as_posix() for p in (root / 'src/pytest_xray').rglob('*.py')}
    if not expected or set(data['files']) != expected or data['meta']['branch_coverage'] is not True:
        raise ValueError('Coverage must include every plugin Python file and branch measurement')
    keys = ('covered_lines', 'num_statements', 'covered_branches', 'num_branches')
    totals = data['totals']
    for key in keys:
        if type(totals[key]) is not int or totals[key] < 0:
            raise ValueError('Invalid coverage count')
        if sum(f['summary'][key] for f in data['files'].values()) != totals[key]:
            raise ValueError('Coverage totals disagree with file measurements')
    if not totals['num_statements'] > 0 or not 0 <= totals['covered_lines'] <= totals['num_statements']:
        raise ValueError('Invalid line coverage counts')
    if not totals['num_branches'] > 0 or not 0 <= totals['covered_branches'] <= totals['num_branches']:
        raise ValueError('Invalid branch coverage counts')
    return dict(
        provenance,
        scope='src/pytest_xray/**/*.py; full pytest suite including Python subprocesses',
        tool='coverage.py ' + data['meta']['version'],
        source_sha256=source_digest(root),
        files=len(expected),
        **{key: totals[key] for key in keys},
        line_percent=round(100 * totals['covered_lines'] / totals['num_statements'], 1),
        branch_percent=round(100 * totals['covered_branches'] / totals['num_branches'], 1),
    )


def render(summary, output):
    output.mkdir(parents=True, exist_ok=True)
    label = 'plugin lines'
    value = f'{summary["line_percent"]:.1f}%'
    title = html.escape(f'{label}: {value}')
    badge = f'''<svg xmlns="http://www.w3.org/2000/svg" width="145" height="20" role="img" aria-label="{title}">
<title>{title}</title><rect width="87" height="20" fill="#555"/><rect x="87" width="58" height="20" fill="#007ec6"/>
<g fill="#fff" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">
<text x="43.5" y="14">{label}</text><text x="116" y="14">{value}</text></g></svg>'''
    (output / 'coverage.svg').write_text(badge)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    details = '\n'.join(f'<dt>{html.escape(str(k))}</dt><dd>{html.escape(str(v))}</dd>' for k, v in summary.items())
    (output / 'index.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>pytest Xray Plus coverage snapshot</title>
<style>body{{font:16px system-ui;max-width:60rem;margin:2rem auto;padding:0 1rem}}
dd{{overflow-wrap:anywhere;margin-bottom:1rem}}</style>
<h1>Plugin coverage snapshot</h1><img src="coverage.svg" alt="{title}">
<p>This is a measured snapshot of the commit below, not necessarily the latest main or PyPI release.</p>
<p><a href="html/index.html">Detailed coverage report</a> · <a href="coverage.json">Raw measurement</a> ·
<a href="summary.json">Snapshot provenance</a></p>
<p>The badge counts executed plugin lines. Branch coverage is reported separately below; the detailed
report's Total percentage includes branches. Tests and repository tools are outside the denominator.
This does not prove live Jira/Xray compatibility, native iteration support or absence of defects.</p>
<dl>{details}</dl></html>''')


def measure(root):
    root = root.resolve()
    if not (root / 'src/pytest_xray').is_dir():
        raise ValueError('Run against a plugin checkout')
    out = root / '.harness/coverage'
    if any(p.is_symlink() for p in (root / '.harness', out, out / 'public')):
        raise ValueError('Coverage output must not be a symlink')
    out.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('XRAY_', 'PYTEST_', 'COVERAGE_'))}
    env['COVERAGE_SRC_ROOT'] = str(root / 'src/pytest_xray')
    # Ensure all pytest subprocesses import this checkout, including --root snapshots.
    env['PYTHONPATH'] = str(root / 'src')
    env['PYTEST_ADDOPTS'] = ''
    with tempfile.TemporaryDirectory(prefix='measurement-', dir=out) as directory:
        temp = Path(directory)
        env['COVERAGE_FILE'] = str(temp / '.coverage')
        public = temp / 'public'
        public.mkdir()
        base = [sys.executable, '-m', 'coverage']
        config = '--rcfile=' + str(CONFIG)
        commands = [
            base + ['run', config, '-m', 'pytest', '-q'],
            base + ['combine', config],
            base + ['json', config, '-o', str(public / 'coverage.json')],
            base + ['html', config, '-d', str(public / 'html')],
        ]
        with (out / 'latest-tests.log').open('w') as log:
            for command in commands:
                subprocess.run(
                    command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=600, check=True
                )
        data = json.loads((public / 'coverage.json').read_text())
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip())
        run_id = os.environ.get('GITHUB_RUN_ID', '')
        provenance = {
            'commit': revision,
            'working_tree_dirty': dirty,
            'measured_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'python': sys.version.split()[0],
            'command': ' '.join([sys.executable, *sys.argv]),
            'measurement_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'measurement_config_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
            'workflow_run': f'https://github.com/matusowskymichael/pytest-Jira-xray-plus/actions/runs/{run_id}'
            if run_id
            else 'local measurement',
        }
        summary = summarize(data, root, provenance)
        render(summary, public)
        target = out / 'public'
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(public), target)
        print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        measure(args.root)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(
            f'Coverage measurement failed ({type(error).__name__}); inspect .harness/coverage/latest-tests.log.',
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
