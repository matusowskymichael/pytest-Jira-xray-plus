"""Check built links, fragments and assets under the real GitHub Pages base path."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'site'
BASE = 'https://matusowskymichael.github.io/pytest-Jira-xray-plus/'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


pages = {p: Page(p.read_text()) for p in ROOT.rglob('*.html')}
errors = []
checked = 0
for path, page in pages.items():
    relative = path.relative_to(ROOT).as_posix()
    url = BASE + (relative.removesuffix('index.html') if path.name == 'index.html' else relative)
    for link in page.links:
        absolute = urljoin(url, link)
        if not absolute.startswith(BASE):
            continue
        parts = urlsplit(absolute)
        target = ROOT / unquote(parts.path.removeprefix(urlsplit(BASE).path))
        if target.is_dir():
            target /= 'index.html'
        checked += 1
        if not target.is_file():
            errors.append(f'{relative}: missing {link}')
        elif parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
            errors.append(f'{relative}: missing anchor {link}')
assert not errors, '\n'.join(errors)
assert (ROOT / 'search/search_index.json').is_file()
print(f'PASS: {len(pages)} HTML pages, {checked} internal links/fragments/assets, search index')
