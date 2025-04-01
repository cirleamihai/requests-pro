import uuid

from tls_client import Session as tlsClient
from urllib.parse import quote

from src.abstractClient import Client
from src.utils.headerTools import HeaderHelper

from src.utils.httpsUtils import is_charles_running


def kwargs_processing(func):
    """
    Decorator function that processes the kwargs before passing them to the requests function.

    Since we are using an entirely different library, some kwargs from the requestHandler might not work properly
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


# noinspection PyTypeChecker
# noinspection PyProtectedMember
class TLSClientSession(Client):
    def __init__(
            self,
            proxies: dict = None,
            headers: dict = None,
            header_helper: HeaderHelper = None,
            client_identifier: str = "chrome_120",
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

        self.session = tlsClient(self.client_identifier,
                                 random_tls_extension_order=True,
                                 header_order=self.header_order,
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

    @kwargs_processing
    def get(self, url: str, **kwargs):
        return self.session.get(url, **kwargs)

    @kwargs_processing
    def post(self, url: str, **kwargs):
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            kwargs['data'] = '&'.join([f"{k}={v}" for k, v in kwargs['data'].items()])
        return self.session.post(url, **kwargs)

    @kwargs_processing
    def put(self, url: str, **kwargs):
        return self.session.put(url, **kwargs)

    @kwargs_processing
    def delete(self, url: str, **kwargs):
        return self.session.delete(url, **kwargs)

    @kwargs_processing
    def options(self, url: str, **kwargs):
        return self.session.options(url, **kwargs)

    def close(self):
        self.session.close()

    def to_json(self):
        """Serialize the session to a JSON-serializable dictionary."""
        data = {
            'sessionClientType': 'TLSClientSession',
            'client_identifier': self.client_identifier,
            'headers': dict(self.headers),
            'cookies': self._serialize_cookies(),
            'proxies': self.proxies,
            'header_helper': self.header_helper.__class__.__name__,
        }
        return data

    @classmethod
    def from_json(cls, data: dict, header_helper: HeaderHelper):
        """Create a TLSClientSession from JSON data."""
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

    def copy_essentials(self, other: "TLSClientSession"):
        super().copy_essentials(other)

        self.header_helper = other.header_helper
        self.client_identifier = other.client_identifier

    def __getattr__(self, name):
        # Delegate attribute access to the underlying session and uncaught properties in the Interface
        return getattr(self.session, name)
