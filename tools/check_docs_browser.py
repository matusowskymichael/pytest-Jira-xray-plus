"""Exercise the static site at its project prefix in Chromium, desktop and mobile."""
import functools
import http.server
import json
import os
from pathlib import Path
import tempfile
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('DOCS_SCREENSHOTS', '/tmp/xray-site-preview'))
OUT.mkdir(parents=True, exist_ok=True)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


with tempfile.TemporaryDirectory() as directory, sync_playwright() as playwright:
    (Path(directory) / 'pytest-Jira-xray-plus').symlink_to(ROOT / 'site', target_is_directory=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=directory))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/pytest-Jira-xray-plus/'
    browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH'), args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1, permissions=['clipboard-read', 'clipboard-write'])
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(base, wait_until='networkidle')
    assert page.title().startswith('pytest Xray Plus')
    assert page.locator('.md-sidebar--primary').is_visible()
    assert page.locator('.md-tabs').is_visible()
    page.screenshot(path=str(OUT / 'desktop-home.png'), full_page=True)
    page.get_by_role('link', name='Start the tutorial', exact=True).click()
    assert page.locator('h1').inner_text().startswith('1. Create a project')
    page.goto(base + 'tutorial/cases/', wait_until='networkidle')
    assert page.locator('.highlight .k').count() > 0  # syntax highlighting
    assert page.locator('button[title="Copy to clipboard"]').count() > 0
    page.locator('button[title="Copy to clipboard"]').first.click()
    assert 'import pytest' in page.evaluate('navigator.clipboard.readText()')
    page.screenshot(path=str(OUT / 'desktop-tutorial.png'), full_page=True)
    search = page.get_by_role('textbox', name='Search', exact=True)
    search.click()
    search.press_sequentially('comment', delay=60)
    page.locator('.md-search-result a[href]').first.wait_for(state='visible', timeout=15000)
    assert page.locator('.md-search-result a[href]').count() > 0
    page.screenshot(path=str(OUT / 'desktop-search.png'), full_page=True)
    page.keyboard.press('Escape')
    page.locator('label[for="__palette_1"]').click()
    assert page.locator('body').get_attribute('data-md-color-scheme') == 'slate'
    mobile = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    m = mobile.new_page()
    m.on('pageerror', lambda error: errors.append(str(error)))
    m.goto(base, wait_until='networkidle')
    assert m.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    m.screenshot(path=str(OUT / 'mobile-home.png'), full_page=True)
    m.locator('.md-header label[for="__drawer"]').click()
    assert m.locator('#__drawer').is_checked()
    m.screenshot(path=str(OUT / 'mobile-menu.png'), full_page=True)
    m.goto(base + 'tutorial/cases/', wait_until='networkidle')
    assert m.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    m.screenshot(path=str(OUT / 'mobile-tutorial.png'), full_page=True)
    assert not errors, errors
    print(json.dumps({'desktop': 'passed', 'mobile': 'passed', 'search': 'passed',
                      'syntax_highlighting': 'passed', 'theme_toggle': 'passed', 'screenshots': str(OUT)}))
    browser.close()
    server.shutdown()
