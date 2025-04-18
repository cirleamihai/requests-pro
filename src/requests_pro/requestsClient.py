from middlewareClient import MiddlewareClient, request_through_middleware
from requests import Session
from response import Response
from utils.headerTools import HeaderHelper
from utils.httpsUtils import is_charles_running


def kwargs_processing(func):
    """
    **MUST COME LAST**,
        as it is directly related to the kwargs of the requests function.

    This is a decorator function that processes the kwargs before passing them to the requests function.
    """

    def wrapper(self, *args, **kwargs):
        if not kwargs.get("verify"):
            kwargs["verify"] = False

            if (
                kwargs.pop("use_mitm_when_active", self.use_mitm_when_active)
            ) and is_charles_running():
                kwargs["proxies"] = {
                    "http": "http://127.0.0.1:8888",
                    "https": "http://127.0.0.1:8888",
                }

        return func(self, *args, **kwargs)

    return wrapper


class RequestsClient(MiddlewareClient):
    """
    A concrete implementation of the Client interface using the requests library.

    Provides cookie persistence, connection-pooling, and configuration to
    the underlying requests library.
    """

    def __init__(
        self,
        proxies: dict = None,
        headers: dict = None,
        header_helper: HeaderHelper = None,
        no_middleware: bool = False,
        use_mitm_when_active: bool = True,
    ):
        super().__init__(no_middleware, use_mitm_when_active)
        self.session = Session()
        self.header_helper: HeaderHelper = header_helper or HeaderHelper()
        self.client_identifier = "128"

        preset_headers = self.header_helper.get_headers(
            client_identifier=self.client_identifier
        )
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

    @request_through_middleware
    @kwargs_processing
    def request(self, method: str, url: str, **kwargs) -> Response:
        return self.session.request(method=method, url=url, **kwargs)

    def close(self):
        self.session.close()

    def reset_client(
        self,
        proxies: dict = None,
        proxy_filename_path: str = "",
        use_proxies: bool = True,
    ):
        self.rotate_ip(proxies, proxy_filename_path)
        proxies = self.proxies if use_proxies else ""
        self.session.close()

        self.session = Session()

        preset_headers = self.header_helper.get_headers(
            client_identifier=self.client_identifier
        )
        self.session.headers.update(preset_headers)
        self.proxies = proxies

    def to_json(self):
        """Serialize the session to a JSON-serializable dictionary."""
        data = {
            "sessionClientType": "RequestsClient",
            "headers": dict(self.headers),
            "cookies": self._serialize_cookies(),
            "proxies": self.proxies,
            "header_helper": self.header_helper.__class__.__name__,
            "no_middleware": self.no_middleware,
            "use_mitm_when_active": self.use_mitm_when_active,
        }

        return data

    @classmethod
    def from_json(cls, data: dict, header_helper: HeaderHelper):
        """Create a TLSClientSession from JSON data."""
        instance = cls(
            header_helper=header_helper,
            no_middleware=data.get("no_middleware", False),
            use_mitm_when_active=data.get("use_mitm_when_active", True),
        )
        instance.headers.update(data["headers"])
        instance.proxies = data["proxies"]
        instance._deserialize_cookies(data["cookies"])

        return instance

    def copy_essentials(self, other: "RequestsClient"):
        super().copy_essentials(other)

        self.header_helper = other.header_helper
        self.client_identifier = other.client_identifier

    def __getattr__(self, name):
        # Delegate attribute access to the underlying session and uncaught properties in the Interface
        return getattr(self.session, name)
