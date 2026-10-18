"""Built-site URL checks must preserve actual filenames and still reject bad links."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).resolve().parents[1] / 'tools/check_docs_links.py'
BASE = '/pytest-Jira-xray-plus/'


def check_site(tmp_path, pages, assets=None, search=True):
    script = tmp_path / 'tools/check_docs_links.py'
    script.parent.mkdir()
    shutil.copyfile(CHECKER, script)
    site = tmp_path / 'site'
    for name, content in {**pages, **(assets or {})}.items():
        path = site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    if search:
        path = site / 'search/search_index.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{}')
    return subprocess.run([sys.executable, str(script)], cwd=tmp_path, text=True, capture_output=True)


@pytest.mark.parametrize('name', [
    'index.html', 'guide/index.html', 'class_index.html', 'coverage/html/function_index.html',
    'coverage/html/class_index.html', 'guide/myindex.html', 'guide/class index.html',
])
@pytest.mark.parametrize('link', ['', '#here', '?view=all#here'])
def test_self_links_resolve_to_the_actual_page(tmp_path, name, link):
    result = check_site(tmp_path, {name: f'<h1 id="here">Page</h1><a href="{link}">Self</a>'})
    assert result.returncode == 0, result.stderr
    assert 'PASS: 1 HTML pages, 1 internal links/fragments/assets' in result.stdout


@pytest.mark.parametrize('name', ['index.html', 'guide/index.html', 'class_index.html', 'coverage/function_index.html'])
def test_missing_self_fragment_is_still_rejected(tmp_path, name):
    result = check_site(tmp_path, {name: '<a href="#missing">Broken</a>'})
    assert result.returncode != 0
    assert f'{name}: missing anchor #missing' in result.stderr


def test_relative_files_assets_encoded_paths_and_fragments(tmp_path):
    result = check_site(tmp_path, {
        'index.html': '<a href="coverage/html/class_index.html#here">Classes</a>',
        'coverage/html/class_index.html': (
            '<h1 id="here">Classes</h1><a href="function_index.html#detail">Functions</a>'
            '<a href="../../guide/">Guide</a><a href="class%20index.html#hello%20world">Encoded</a>'
            '<img src="../assets/icon.svg"><script src="../assets/app.js"></script>'
        ),
        'coverage/html/function_index.html': (
            '<h1 id="detail">Functions</h1><a href="class_index.html#here">Classes</a>'
        ),
        'coverage/html/class index.html': '<h1 id="hello world">Encoded anchor</h1><a href="#hello%20world">Self</a>',
        'guide/index.html': f'<a href="{BASE}coverage/html/class_index.html?view=all#here">Classes</a>',
    }, assets={'coverage/assets/icon.svg': '<svg/>', 'coverage/assets/app.js': 'void 0;'})
    assert result.returncode == 0, result.stderr
    assert 'PASS: 5 HTML pages, 9 internal links/fragments/assets' in result.stdout


@pytest.mark.parametrize('markup,missing', [
    ('<a href="absent.html">Missing page</a>', 'absent.html'),
    ('<img src="absent.svg">', 'absent.svg'),
    ('<script src="absent.js"></script>', 'absent.js'),
    ('<a href="missing%20page.html#here">Missing encoded page</a>', 'missing%20page.html#here'),
])
def test_missing_relative_targets_remain_failures(tmp_path, markup, missing):
    result = check_site(tmp_path, {'coverage/html/class_index.html': markup})
    assert result.returncode != 0
    assert f'coverage/html/class_index.html: missing {missing}' in result.stderr


def test_linked_page_missing_fragment_remains_failure(tmp_path):
    result = check_site(tmp_path, {
        'class_index.html': '<a href="function_index.html#absent">Missing fragment</a>',
        'function_index.html': '<h1 id="present">Functions</h1>',
    })
    assert result.returncode != 0
    assert 'class_index.html: missing anchor function_index.html#absent' in result.stderr


def test_external_links_keep_existing_project_boundary(tmp_path):
    result = check_site(tmp_path, {'class_index.html': (
        '<a href="https://example.invalid/missing">External</a>'
        '<a href="https://matusowskymichael.github.io/another-project/missing">Other project</a>'
        '<a href="mailto:synthetic@example.invalid">Mail</a>'
    )})
    assert result.returncode == 0, result.stderr
    assert '0 internal links/fragments/assets' in result.stdout


def test_search_index_is_still_required(tmp_path):
    result = check_site(tmp_path, {'class_index.html': '<h1>Classes</h1>'}, search=False)
    assert result.returncode != 0
    assert 'search/search_index.json' in result.stderr
