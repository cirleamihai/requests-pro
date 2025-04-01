from requests import Session

from src.middlewareClient import MiddlewareClient
from src.utils.headerTools import HeaderHelper

from src.utils.httpsUtils import is_charles_running


def kwargs_processing(func):
    """
    Decorator function that processes the kwargs before passing them to the requests function.

    Since we are using an entirely different library, some kwargs from the requestHandler might not work properly
    """

    def wrapper(self, *args, **kwargs):
        if 'verify' in kwargs:
            kwargs['verify'] = False

            if is_charles_running():
                kwargs['proxies'] = {
                    "http": "http://127.0.0.1:8888",
                    "https": "http://127.0.0.1:8888",
                }

        return func(self, *args, **kwargs)

    return wrapper


class RequestsClient(MiddlewareClient):
    """
    Concrete implementation of the Client interface using the requests library Session feature.
    """

    def __init__(
            self,
            proxies: dict = None,
            headers: dict = None,
            header_helper: HeaderHelper = None,
    ):
        super().__init__()
        self.session = Session()
        self.header_helper: HeaderHelper = header_helper or HeaderHelper()
        self.client_identifier = "128"

        preset_headers = self.header_helper.get_headers(client_identifier=self.client_identifier)
        self.session.headers.update(preset_headers)

        if proxies:
            self.session.proxies = proxies

        if headers:
            self.session.headers.update(headers)

    def update_headers(self, new_headers: dict):
        self.session.headers.update(new_headers)

    def set_new_headers(self, new_headers: dict):
        self.session.headers = new_headers

    def set_cookie(self, name, value, domain):
        self.session.cookies.set(name=name, value=value, domain=domain)

    def set_cookies(self, cookies: dict):
        self.session.cookies.update(cookies)

    @kwargs_processing
    def get(self, url: str, **kwargs):
        return self.session.get(url, **kwargs)

    @kwargs_processing
    def post(self, url: str, **kwargs):
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

    def reset_client(self, use_proxies: bool = True):
        self.rotate_ip()
        proxies = self.proxies if use_proxies else ""

        self.session = Session()

        if self.header_helper:
            preset_headers = self.header_helper.get_headers(client_identifier=self.client_identifier)
            self.session.headers.update(preset_headers)

        self.proxies = proxies

    def to_json(self):
        """Serialize the session to a JSON-serializable dictionary."""
        data = {
            'sessionClientType': 'RequestsClient',
            'headers': dict(self.headers),
            'cookies': self._serialize_cookies(),
            'proxies': self.proxies,
            'header_helper': self.header_helper.__class__.__name__,
        }

        return data

    @classmethod
    def from_json(cls, data: dict, header_helper: HeaderHelper):
        """Create a TLSClientSession from JSON data."""
        instance = cls(header_helper=header_helper)
        instance.headers.update(data['headers'])
        instance.proxies = data['proxies']
        instance._deserialize_cookies(data['cookies'])

        return instance

    def copy_essentials(self, other: "RequestsClient"):
        super().copy_essentials(other)

        self.header_helper = other.header_helper
        self.client_identifier = other.client_identifier

    def __getattr__(self, name):
        # Delegate attribute access to the underlying session and uncaught properties in the Interface
        return getattr(self.session, name)
