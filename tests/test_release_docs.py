"""The site must display current release notes as well as older fork notes."""

import shutil
import subprocess
import sys
from pathlib import Path


def test_generated_changelog_contains_current_and_unreleased_notes(tmp_path):
    root = Path(__file__).parents[1]
    for name in ['README.md', 'CHANGELOG.rst', 'docs/CASE-REPORT.md', 'tools/prepare_docs_site.py']:
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, destination)
    shutil.copytree(root / 'website', tmp_path / 'website')
    subprocess.run([sys.executable, str(tmp_path / 'tools/prepare_docs_site.py')], check=True, capture_output=True)
    rendered = (tmp_path / '.docs-source/project/changelog.md').read_text()
    assert '## Unreleased' in rendered and 'explicit permission confirmation' in rendered
    assert '## 0.1.9 [2026-10-17]' in rendered and 'Omit xdist worker-header-only comments' in rendered
    assert 'Preserve opt-in reports when integer parameters' in rendered
    assert 'Create missing parent folders' in rendered
    assert 'Avoid repeated linear Test-key scans' in rendered
    assert 'Reject empty or whitespace-only upload base URLs' in rendered
    assert '## 0.1.8 [2026-10-17]' in rendered and 'Report expected path expansion' in rendered
    assert '## 0.1.7 [2026-10-17]' in rendered and 'Classify disallowed duplicate Test keys' in rendered
    assert '## 0.1.6 [2026-10-16]' in rendered and 'shared README badges' in rendered
    assert '## 0.1.5 [2026-10-16]' in rendered and 'Validate malformed defects' in rendered
    assert '## 0.1.4 [2026-10-16]' in rendered and '## 0.1.3 (2026-10-15)' in rendered
    assert '0.9.4 [2026-04-24]' not in rendered
    assert (
        rendered.index('## Unreleased')
        < rendered.index('## 0.1.9')
        < rendered.index('## 0.1.8')
        < rendered.index('## 0.1.7')
        < rendered.index('## 0.1.6')
        < rendered.index('## 0.1.5')
        < rendered.index('## 0.1.4')
    )
