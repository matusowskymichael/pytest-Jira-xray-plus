"""Badges must derive from complete, consistent plugin coverage data."""

import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    'measure_coverage', Path(__file__).parents[1] / 'tools/measure_coverage.py'
)
assert SPEC is not None and SPEC.loader is not None
coverage_report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coverage_report)


@pytest.fixture
def measurement(tmp_path):
    source = tmp_path / 'src/pytest_xray'
    source.mkdir(parents=True)
    (source / 'sample.py').write_text('a = 1\nb = 2\nc = 3\nd = 4\n')
    totals = {'covered_lines': 3, 'num_statements': 4, 'covered_branches': 1, 'num_branches': 2}
    data = {
        'meta': {'branch_coverage': True, 'version': 'synthetic'},
        'totals': totals,
        'files': {'src/pytest_xray/sample.py': {'summary': dict(totals)}},
    }
    return tmp_path, data


def test_line_badge_is_measured_separately_from_branches(measurement):
    root, data = measurement
    result = coverage_report.summarize(data, root, {'commit': 'a' * 40})
    assert result['line_percent'] == 75.0 and result['branch_percent'] == 50.0
    output = root / 'report'
    coverage_report.render(result, output)
    image = ET.fromstring((output / 'coverage.svg').read_text())
    assert image.attrib['aria-label'] == 'plugin lines: 75.0%'
    assert json.loads((output / 'summary.json').read_text()) == result
    page = (output / 'index.html').read_text()
    assert 'not necessarily the latest main or PyPI release' in page
    assert 'html/index.html' in page and 'coverage.json' in page


@pytest.mark.parametrize(
    'problem',
    [
        'missing_file',
        'foreign_file',
        'no_branches',
        'invalid_count',
        'inconsistent_totals',
        'too_many_lines',
        'too_many_branches',
        'zero_statements',
    ],
)
def test_invalid_measurement_cannot_generate_badge(measurement, problem):
    root, data = measurement
    if problem == 'missing_file':
        (root / 'src/pytest_xray/unmeasured.py').touch()
    elif problem == 'foreign_file':
        data['files']['tests/test_example.py'] = data['files']['src/pytest_xray/sample.py']
    elif problem == 'no_branches':
        data['meta']['branch_coverage'] = False
    else:
        key, value = {
            'invalid_count': ('covered_lines', -1),
            'inconsistent_totals': ('covered_lines', 2),
            'too_many_lines': ('covered_lines', 5),
            'too_many_branches': ('covered_branches', 3),
            'zero_statements': ('num_statements', 0),
        }[problem]
        data['totals'][key] = value
        if problem != 'inconsistent_totals':
            data['files']['src/pytest_xray/sample.py']['summary'][key] = value
    with pytest.raises(ValueError):
        coverage_report.summarize(data, root, {})


def test_report_escapes_provenance_text(measurement):
    root, data = measurement
    result = coverage_report.summarize(data, root, {'commit': '<script>unsafe</script>'})
    coverage_report.render(result, root / 'report')
    page = (root / 'report/index.html').read_text()
    assert '<script>' not in page and '&lt;script&gt;' in page


def test_shared_readme_badges_point_to_real_project_metadata():
    root = Path(__file__).parents[1]
    readme = (root / 'README.md').read_text()
    badges = re.findall(r'\[!\[([^]]+)\]\(([^)]+)\)\]\(([^)]+)\)', readme)
    assert len(badges) == 6
    assert all(image.startswith('https://') and link.startswith('https://') for _, image, link in badges)
    assert all('pytest-jira-xray-plus' in link.lower() for _, _, link in badges)
    assert not any('discord' in image.lower() or 'codecov' in image.lower() for _, image, _ in badges)
    assert 'coverage/coverage.svg' in badges[-1][1]
    workflow = (root / '.github/workflows/tests.yml').read_text()
    for version in ['3.12', '3.13', '3.14']:
        assert f"'{version}'" in workflow
    assert 'python tools/measure_coverage.py' in workflow
    assert 'contents: write' not in workflow and 'id-token: write' not in workflow


@pytest.fixture
def metadata_case(tmp_path):
    spec = importlib.util.spec_from_file_location('status_badges', Path(__file__).parents[1] / 'tools/status_badges.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    workflow = tmp_path / '.github/workflows/tests.yml'
    workflow.parent.mkdir(parents=True)
    workflow.write_text("matrix:\n  python: ['3.12', '3.13', '3.14']\n")
    data = {
        'info': {'name': 'pytest-jira-xray-plus', 'version': '0.1.5', 'license_expression': 'Apache-2.0'},
        'urls': [{'yanked': False}],
    }
    return module, tmp_path, data


def test_metadata_badges_come_from_verified_package_and_matrix(metadata_case):
    module, root, data = metadata_case
    result = module.write_badges(root, data, root / 'public')
    assert result['published_version'] == '0.1.5' and result['tested_python'] == ['3.12', '3.13', '3.14']
    image = ET.fromstring((root / 'public/pypi.svg').read_text())
    assert image.attrib['aria-label'] == 'PyPI snapshot: 0.1.5'
    assert 'not live service queries' in (root / 'public/index.html').read_text()


@pytest.mark.parametrize('problem', ['wrong_package', 'prerelease', 'licence', 'yanked', 'missing_files', 'matrix'])
def test_unverified_metadata_cannot_create_badges(metadata_case, problem):
    module, root, data = metadata_case
    if problem == 'wrong_package':
        data['info']['name'] = 'pytest'
    elif problem == 'prerelease':
        data['info']['version'] = '0.1.6a1'
    elif problem == 'licence':
        data['info']['license_expression'] = 'unknown'
    elif problem == 'yanked':
        data['urls'][0]['yanked'] = True
    elif problem == 'missing_files':
        data['urls'] = []
    else:
        (root / '.github/workflows/tests.yml').write_text('matrix: unsupported')
    with pytest.raises(ValueError):
        module.write_badges(root, data, root / 'public')
    assert not (root / 'public').exists()
