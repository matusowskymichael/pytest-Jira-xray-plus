# Modified in the parameter-details prototype; see NOTICE.
from pathlib import Path
from typing import Union

import pytest
from requests.auth import AuthBase

from pytest_xray import hooks
from pytest_xray.case_report import CaseReportPlugin
from pytest_xray.constant import (
    JIRA_API_KEY,
    JIRA_CLIENT_SECRET_AUTH,
    JIRA_CLOUD,
    JIRA_XRAY_FLAG,
    TEST_EXECUTION_ENDPOINT,
    TEST_EXECUTION_ENDPOINT_CLOUD,
    XRAY_ADD_CAPTURES,
    XRAY_ALLOW_DUPLICATE_IDS,
    XRAY_EXECUTION_ID,
    XRAY_PLUGIN,
    XRAY_TEST_PLAN_ID,
    XRAYPATH,
)
from pytest_xray.file_publisher import FilePublisher
from pytest_xray.helper import get_api_key_auth, get_basic_auth, get_bearer_auth
from pytest_xray.xray_plugin import Publisher, XrayPlugin
from pytest_xray.xray_publisher import ApiKeyAuth, ClientSecretAuth, XrayPublisher


def pytest_addoption(parser: pytest.Parser) -> None:
    xray = parser.getgroup('Jira Xray report')
    xray.addoption(
        '--xray-case-report',
        metavar='path',
        default=None,
        help='Write a transport-independent offline JSON case report',
    )
    xray.addoption(
        '--xray-case-values',
        action='store_true',
        default=False,
        help='Opt in to potentially sensitive scalar values in the offline case report',
    )
    xray.addoption(
        '--xray-case-redact-identities',
        action='store_true',
        default=False,
        help='Replace offline node and parameter IDs with per-run opaque aliases',
    )
    xray.addoption(
        '--xray-parameter-details',
        action='store_true',
        default=False,
        help='Include parameter case identity, values and phase outcomes in test run comments',
    )
    xray.addoption(JIRA_XRAY_FLAG, action='store_true', default=False, help='Upload test results to JIRA XRAY')
    xray.addoption(JIRA_CLOUD, action='store_true', default=False, help='Use with JIRA XRAY cloud server')
    xray.addoption(
        JIRA_API_KEY,
        action='store_true',
        default=False,
        help='Use Jira API Key authentication',
    )
    xray.addoption(
        JIRA_CLIENT_SECRET_AUTH,
        action='store_true',
        default=False,
        help='Use client secret authentication',
    )
    xray.addoption(
        XRAY_EXECUTION_ID, action='store', metavar='ExecutionId', default=None, help='XRAY Test Execution ID'
    )
    xray.addoption(XRAY_TEST_PLAN_ID, action='store', metavar='TestplanId', default=None, help='XRAY Test Plan ID')
    xray.addoption(
        XRAYPATH,
        action='store',
        metavar='path',
        default=None,
        help='Do not upload to a server but create JSON report file at given path',
    )
    xray.addoption(
        XRAY_ALLOW_DUPLICATE_IDS,
        action='store_true',
        default=False,
        help='Allow test ids to be present on multiple pytest tests',
    )
    xray.addoption(
        XRAY_ADD_CAPTURES,
        action='store_true',
        default=False,
        help='Add captures from log, stdout or/and stderr, to the report comment field',
    )


def pytest_addhooks(pluginmanager):
    pluginmanager.add_hookspecs(hooks)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line('markers', 'xray(JIRA_ID): mark test with JIRA XRAY test case ID')
    if config.option.collectonly:
        return

    case_path = config.getoption('--xray-case-report')
    redact_ids = config.getoption('--xray-case-redact-identities')
    if redact_ids and not case_path:
        raise pytest.UsageError('--xray-case-redact-identities requires --xray-case-report')
    if redact_ids and config.getoption('--xray-case-values'):
        raise pytest.UsageError('--xray-case-redact-identities cannot be combined with --xray-case-values')
    if config.getoption('--xray-case-values') and not case_path:
        raise pytest.UsageError('--xray-case-values requires --xray-case-report')
    if case_path:
        xray_path = config.getoption(XRAYPATH)
        if xray_path and Path(case_path).expanduser().resolve() == Path(xray_path).expanduser().resolve():
            raise pytest.UsageError('--xray-case-report and --xraypath must use different files')
        config.pluginmanager.register(
            CaseReportPlugin(config, case_path, config.getoption('--xray-case-values'), redact_ids),
            name='xray-offline-cases',
        )

    if not config.getoption(JIRA_XRAY_FLAG):
        return

    xray_path = config.getoption(XRAYPATH)

    if xray_path:
        publisher: Publisher = FilePublisher(xray_path)
    else:
        endpoint = TEST_EXECUTION_ENDPOINT_CLOUD if config.getoption(JIRA_CLOUD) else TEST_EXECUTION_ENDPOINT

        if config.getoption(JIRA_CLIENT_SECRET_AUTH):
            options = get_bearer_auth()
            auth: Union[AuthBase, tuple[str, str]] = ClientSecretAuth(
                options['BASE_URL'], options['CLIENT_ID'], options['CLIENT_SECRET'], options['VERIFY']
            )
        elif config.getoption(JIRA_API_KEY):
            options = get_api_key_auth()
            auth = ApiKeyAuth(options['API_KEY'])
        else:
            options = get_basic_auth()
            auth = (options['USER'], options['PASSWORD'])

        publisher = XrayPublisher(base_url=options['BASE_URL'], endpoint=endpoint, auth=auth, verify=options['VERIFY'])

    plugin = XrayPlugin(config, publisher)
    config.pluginmanager.register(plugin=plugin, name=XRAY_PLUGIN)
