"""Synthetic collection benchmark; comparison counts, never timing thresholds.

Run from a development checkout: python tools/benchmark_collection.py
The list baseline reproduces 0.1.6 membership; the candidate calls the real
validator. Unique deterministic hashes exclude collision effects. This measures
only duplicate validation, not full pytest collection or live Jira/Xray.
"""

import json
from types import SimpleNamespace

from pytest_xray.xray_plugin import XrayPlugin


class Key(str):
    comparisons = 0
    hashes = 0

    def __eq__(self, other):
        type(self).comparisons += 1
        return super().__eq__(other)

    def __hash__(self):
        type(self).hashes += 1
        return int(self.split('-')[1])


def baseline(plugin, items):
    seen = []
    duplicates = []
    for item in items:
        for key in plugin._get_test_keys(item):
            if key in seen:
                duplicates.append(key)
            else:
                seen.append(key)
        assert not duplicates  # This benchmark deliberately supplies unique keys.


def main():
    plugin = object.__new__(XrayPlugin)
    rows = []
    for allow in (False, True):
        plugin.allow_duplicate_ids = allow
        for size in (128, 256, 512, 1024):
            items = []
            for n in range(size):
                marker = SimpleNamespace(args=(Key(f'DEMO-{n}'),), kwargs={})
                items.append(SimpleNamespace(get_closest_marker=lambda name, marker=marker: marker))
            for label, run in [
                ('0.1.6 list baseline', lambda items=items: baseline(plugin, items)),
                ('candidate', lambda items=items: plugin._verify_jira_ids_for_items(items)),
            ]:
                Key.comparisons = Key.hashes = 0
                run()
                rows.append(
                    dict(
                        implementation=label,
                        allow_duplicates=allow,
                        keys=size,
                        equality_comparisons=Key.comparisons,
                        hash_calls=Key.hashes,
                    )
                )
    print(
        json.dumps({'scope': 'Synthetic unique-key validation; no timing or server claims', 'results': rows}, indent=2)
    )


if __name__ == '__main__':
    main()
