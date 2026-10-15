import json
from typing import Any, Callable, Optional, Union

import requests
from requests import PreparedRequest
from requests.auth import AuthBase

from pytest_xray.constant import AUTHENTICATE_ENDPOINT
from pytest_xray.exceptions import XrayError

AuthType = Optional[Union[tuple[str, str], AuthBase, Callable[[PreparedRequest], PreparedRequest]]]


# Connect timeout and read inactivity timeout, not a total wall-clock deadline.
REQUEST_TIMEOUT = (10, 60)


class ClientSecretAuth(AuthBase):
    """Bearer authentication with Client ID and a Client Secret."""

    def __init__(self, base_url: str, client_id: str, client_secret: str, verify: Union[bool, str] = True) -> None:
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.verify = verify

    @property
    def endpoint_url(self) -> str:
        return f'{self.base_url}{AUTHENTICATE_ENDPOINT}'

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        auth_data = {'client_id': self.client_id, 'client_secret': self.client_secret}

        try:
            response = requests.post(
                self.endpoint_url,
                data=json.dumps(auth_data),
                headers=headers,
                verify=self.verify,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
            response.raise_for_status()
            if response.status_code != 200:
                raise XrayError('Authentication did not return HTTP 200')
            auth_token = response.json()
            if not isinstance(auth_token, str) or not auth_token.strip() or any(c.isspace() for c in auth_token):
                raise XrayError('Authentication returned an invalid token')
        except requests.exceptions.RequestException as exc:
            raise XrayError(f'{type(exc).__name__}: cannot authenticate with Xray') from exc
        except ValueError as exc:
            raise XrayError('Authentication returned invalid JSON') from exc
        r.headers['Authorization'] = f'Bearer {auth_token}'
        return r


class ApiKeyAuth(AuthBase):
    """Personal access token authentication."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers['Authorization'] = f'Bearer {self.api_key}'
        return r


class XrayPublisher:
    """Exports Xray report to a Jira server."""

    def __init__(self, base_url: str, endpoint: str, auth: AuthType, verify: Union[bool, str] = True) -> None:
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        self.base_url = base_url
        self.endpoint = endpoint
        self.auth = auth
        self.verify = verify

    @property
    def endpoint_url(self) -> str:
        """Return full URL to the server."""
        return self.base_url + self.endpoint

    def _send_data(self, url: str, auth: AuthType, data: dict[str, Any]) -> dict[str, Any]:
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        try:
            response = requests.request(
                method='POST',
                url=url,
                headers=headers,
                json=data,
                auth=auth,
                verify=self.verify,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
            )
            response.raise_for_status()
            if not 200 <= response.status_code < 300:
                raise XrayError(f'Xray import returned unexpected HTTP {response.status_code}; redirects are disabled')
            result = response.json()
        except requests.exceptions.HTTPError as exc:
            raise XrayError(f'HTTPError: Could not post to Xray. Response status code: {response.status_code}') from exc
        except requests.exceptions.RequestException as exc:
            raise XrayError(f'{type(exc).__name__}: cannot post results to Xray') from exc
        except ValueError as exc:
            raise XrayError('Xray import returned invalid JSON') from exc
        if not isinstance(result, dict):
            raise XrayError('Xray import response must be a JSON object')
        return result

    def publish(self, data: dict[str, Any]) -> str:
        """Publish once; never retry a potentially accepted import automatically."""
        response_data = self._send_data(self.endpoint_url, self.auth, data)
        try:
            key = response_data['testExecIssue']['key'] if 'testExecIssue' in response_data else response_data['key']
        except (KeyError, TypeError):
            raise XrayError('Cannot read Test Execution ID from server response') from None
        if not isinstance(key, str) or not key.strip():
            raise XrayError('Cannot read Test Execution ID from server response')
        return key
