"""Build reproducible release archives locally; never upload (Apache-2.0)."""

import gzip
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

EPOCH = 1792022400  # 2026-10-15 UTC; fixed release timestamp
root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / 'release-dist'
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as directory:
    staging = Path(directory) / 'source'
    staging.mkdir()
    for name in ['pyproject.toml', 'MANIFEST.in', 'LICENSE', 'NOTICE', 'README.md', 'README.rst', 'CHANGELOG.rst']:
        shutil.copyfile(root / name, staging / name)
    for name in ['src', 'docs', 'tests', 'tools', 'examples']:
        shutil.copytree(root / name, staging / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.egg-info', '.pytest_cache'))
    for path in staging.rglob('*'):
        os.utime(path, (EPOCH, EPOCH))
        path.chmod(0o755 if path.is_dir() else 0o644)
    build_out = Path(directory) / 'dist'
    env = dict(os.environ, SOURCE_DATE_EPOCH=str(EPOCH), PYTHONHASHSEED='0')
    subprocess.run([sys.executable, '-m', 'build', '--no-isolation', '--outdir', str(build_out), str(staging)],
                   env=env, check=True)
    for archive in sorted(build_out.iterdir()):
        target = out / archive.name
        if archive.name.endswith('.tar.gz'):
            # setuptools sdist header timestamps/ownership vary by machine.
            buffer = io.BytesIO()
            with tarfile.open(archive, 'r:gz') as source, tarfile.open(fileobj=buffer, mode='w') as dest:
                for member in sorted(source.getmembers(), key=lambda item: item.name):
                    member.mtime = EPOCH
                    member.uid = member.gid = 0
                    member.uname = member.gname = ''
                    member.mode = 0o755 if member.isdir() else 0o644
                    member.pax_headers = {}
                    dest.addfile(member, source.extractfile(member) if member.isfile() else None)
            with target.open('wb') as stream, gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=EPOCH) as gz:
                gz.write(buffer.getvalue())
        else:
            shutil.copyfile(archive, target)
        print(hashlib.sha256(target.read_bytes()).hexdigest(), target.name)
