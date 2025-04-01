import uuid
from typing import Optional, Dict, List
from urllib.parse import quote

from tls_client import Session as tlsClient
from tls_client.settings import ClientIdentifiers

from middlewareClient import MiddlewareClient, request_through_middleware
from utils.headerTools import HeaderHelper
from utils.httpsUtils import is_charles_running


def kwargs_processing(func):
    """
    **MUST COME BEFORE ANY OTHER DECORATOR**,
        as it is directly related to the kwargs of the requests function.

    This is a decorator function that processes the kwargs before passing them to the requests function.
    """

    def wrapper(self, url: str, **kwargs):
        # Rename the timeout keyword to timeout_seconds
        if 'timeout' in kwargs:
            kwargs['timeout_seconds'] = kwargs.pop('timeout')

        if 'verify' in kwargs:
            kwargs['insecure_skip_verify'] = not kwargs.pop('verify')

            if is_charles_running():
                kwargs['proxy'] = {
                    "http": "http://127.0.0.1:8888",
                    "https": "http://127.0.0.1:8888",
                }

        # Encoding the url
        encoded_url = quote(url, safe=':/?&=%.,/;')

        return func(self, encoded_url, **kwargs)

    return wrapper


class TLSClient(MiddlewareClient):
    """
    A concrete implementation of the Client interface using the tls_client library.

    Provides cookie persistence, connection-pooling, configuration and most importantly,
        low level details that can be configured with the underlying tls_client library.
    """

    def __init__(
            self,
            proxies: dict = None,
            headers: dict = None,
            header_helper: HeaderHelper = None,
            client_identifier: ClientIdentifiers = "chrome_120",
            ja3_string: Optional[str] = None,
            h2_settings: Optional[Dict[str, int]] = None,
            h2_settings_order: Optional[List[str]] = None,
            supported_signature_algorithms: Optional[List[str]] = None,
            supported_delegated_credentials_algorithms: Optional[List[str]] = None,
            supported_versions: Optional[List[str]] = None,
            key_share_curves: Optional[List[str]] = None,
            cert_compression_algo: str = None,
            additional_decode: str = None,
            pseudo_header_order: Optional[List[str]] = None,
            connection_flow: Optional[int] = None,
            priority_frames: Optional[list] = None,
            header_priority: Optional[List[str]] = None,
            force_http1: Optional = False,
            catch_panics: Optional = False,
            debug: Optional = False,
            certificate_pinning: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Currently using this tls client as a wrapper around the requests library:
            https://github.com/FlorianREGAZ/Python-Tls-Client
                which is inspired by https://github.com/bogdanfinn/tls-client

        Currently using chrome 120 which is the default. You can use whatever client_identifier you may want to.
        """
        super().__init__()
        self.client_identifier = client_identifier

        # Getting the header order from the header helper
        self.header_helper: HeaderHelper = header_helper or HeaderHelper()
        self.header_order = self.header_helper.get_header_order()

        self.session = tlsClient(
            client_identifier=self.client_identifier,
            random_tls_extension_order=True,
            header_order=self.header_order,
            # Additional parameters that can be passed to the tls client
            ja3_string=ja3_string,
            h2_settings=h2_settings,
            h2_settings_order=h2_settings_order,
            supported_signature_algorithms=supported_signature_algorithms,
            supported_delegated_credentials_algorithms=supported_delegated_credentials_algorithms,
            supported_versions=supported_versions,
            key_share_curves=key_share_curves,
            cert_compression_algo=cert_compression_algo,
            additional_decode=additional_decode,
            pseudo_header_order=pseudo_header_order,
            connection_flow=connection_flow,
            priority_frames=priority_frames,
            header_priority=header_priority,
            force_http1=force_http1,
            catch_panics=catch_panics,
            debug=debug,
            certificate_pinning=certificate_pinning,
        )

        if proxies:
            self.proxies = proxies

        if headers:
            self.session.headers.update(headers)

        # Create a real user agent to match the tls client identifier
        preset_headers = self.header_helper.get_headers(self.client_identifier)
        self.headers.update(preset_headers)

    def update_headers(self, new_headers: dict):
        self.session.headers.update(new_headers)

    def set_new_headers(self, new_headers: dict):
        self.session.headers = new_headers

    def set_cookie(self, name, value, domain):
        self.cookies.set(name=name, value=value, domain=domain)

        # reset session id to force the client to refresh cookies
        self.session._session_id = str(uuid.uuid4())

    def delete_cookies(self, cookies_list: str | list):
        super().delete_cookies(cookies_list)

        # reset session id to force the client to refresh cookies
        self.session._session_id = str(uuid.uuid4())

    def clear_cookies(self, skip_these: str | list = ""):
        super().clear_cookies(skip_these)

        # reset session id to force the client to refresh cookies
        self.session._session_id = str(uuid.uuid4())

    def set_cookies(self, cookies: dict):
        self.cookies.update(cookies)

        # reset session id to force the client to refresh cookies
        self.session._session_id = str(uuid.uuid4())

    @request_through_middleware
    @kwargs_processing
    def get(self, url: str, **kwargs):
        return self.session.get(url, **kwargs)

    @request_through_middleware
    @kwargs_processing
    def post(self, url: str, **kwargs):
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            kwargs['data'] = '&'.join([f"{k}={v}" for k, v in kwargs['data'].items()])
        return self.session.post(url, **kwargs)

    @request_through_middleware
    @kwargs_processing
    def put(self, url: str, **kwargs):
        return self.session.put(url, **kwargs)

    @request_through_middleware
    @kwargs_processing
    def delete(self, url: str, **kwargs):
        return self.session.delete(url, **kwargs)

    @request_through_middleware
    @kwargs_processing
    def options(self, url: str, **kwargs):
        return self.session.options(url, **kwargs)

    def close(self):
        self.session.close()

    def to_json(self):
        """Serialize the session to a JSON-serializable dictionary."""
        data = {
            'sessionClientType': 'TLSClient',
            'client_identifier': self.client_identifier,
            'headers': dict(self.headers),
            'cookies': self._serialize_cookies(),
            'proxies': self.proxies,
            'header_helper': self.header_helper.__class__.__name__,
        }
        return data

    @classmethod
    def from_json(cls, data: dict, header_helper: HeaderHelper):
        """Create a TLSClient from JSON data."""
        instance = cls(header_helper=header_helper, client_identifier=data.get('client_identifier', "chrome_120"))
        if data.get("client_identifier"):
            instance.headers.update(data['headers'])
        instance.proxies = data.get('proxies', {})
        instance._deserialize_cookies(data.get('cookies', {}))

        return instance

    def reset_client(self, use_proxies: bool = True, proxies: dict = None):
        self.rotate_ip()
        proxies = (proxies or self.proxies) if use_proxies else ""
        self.session.close()

        self.session = tlsClient(self.client_identifier,
                                 random_tls_extension_order=True,
                                 header_order=self.header_helper.get_header_order(),
                                 )

        preset_headers = self.header_helper.get_headers(client_identifier=self.client_identifier)
        self.session.headers.update(preset_headers)
        self.proxies = proxies

    def copy_essentials(self, other: "TLSClient"):
        super().copy_essentials(other)

        self.header_helper = other.header_helper
        self.client_identifier = other.client_identifier

    def __getattr__(self, name):
        # Delegate attribute access to the underlying session and uncaught properties in the Interface
        return getattr(self.session, name)
