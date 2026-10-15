"""Client-side payload policy, not a claimed Jira/Xray server limit."""

from pytest_xray.exceptions import XrayError

DEFAULT_COMMENT_LIMIT = 32_000
TRUNCATION_NOTICE = '\n[TRUNCATED by pytest-jira-xray-plus; full text is in the local full-report archive.]'


def bound_comments(results, limit, archive_path):
    """Return a copy with bounded UTF-8 comments; require lossless retention first."""
    oversized = [test for test in results['tests'] if len(test.get('comment', '').encode('utf-8')) > limit]
    if oversized and not archive_path:
        raise XrayError(
            'Comment exceeds --xray-comment-limit; export withheld. '
            'Set --xray-full-report=PATH to retain the complete payload before truncation.'
        )
    if archive_path:
        from pytest_xray.file_publisher import FilePublisher

        FilePublisher(archive_path).publish(results)
    bounded = dict(results, tests=[])
    for test in results['tests']:
        item = dict(test)
        comment = item.get('comment', '')
        if len(comment.encode('utf-8')) > limit:
            # Keep the inherited wiki noformat block balanced when shortening it.
            closing = '{noformat}' if comment.startswith('{noformat:') and comment.endswith('{noformat}') else ''
            suffix = TRUNCATION_NOTICE + closing
            prefix = comment.encode('utf-8')[: limit - len(suffix.encode('utf-8'))].decode('utf-8', errors='ignore')
            item['comment'] = prefix + suffix
        bounded['tests'].append(item)
    return bounded, len(oversized)
