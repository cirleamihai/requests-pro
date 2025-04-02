from abc import ABC, abstractmethod
from http.cookiejar import Cookie
from typing import Any, Callable, Optional, TypedDict, Unpack

from response import Response
from utils.headerTools import HeaderHelper
from utils.proxiesHandler import ProxiesHandler


class RequestParams(TypedDict, total=False):
    params: dict[str, Any]
    data: Any
    headers: dict[str, str]
    cookies: dict[str, str]
    json: Any
    timeout: float
    proxies: dict[str, str]
    verify: bool

    # These override the class defaults
    no_middleware: bool
    use_mitm_when_active: bool

    # Middleware specific
    middl_max_retries: int
    middl_skip_status_check: bool
    middl_skip_redirects: bool
    middl_custom_status_handling_function: Callable
    middl_redirect_endpoint_stop: str
    middl_redirect_endpoint_contains_stop: str
    middl_statuses_to_skip: list[int | str]


# noinspection PyProtectedMember,PyIncorrectDocstring
class Client(ABC):
    """Interface for the client session classes."""

    def __init__(self, no_middleware: bool = False, use_mitm_when_active: bool = True):
        self.session = None
        self.no_middleware = no_middleware
        self.use_mitm_when_active = use_mitm_when_active

    @abstractmethod
    def update_headers(self, new_headers: dict):
        pass

    @abstractmethod
    def set_new_headers(self, new_headers: dict):
        pass

    @abstractmethod
    def __getattr__(self, name):
        pass

    @abstractmethod
    def set_cookies(self, cookies: dict):
        pass

    @abstractmethod
    def set_cookie(self, name, value, domain):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def reset_client(
        self,
        proxies: dict = None,
        proxy_filename_path: str = "",
        use_proxies: bool = True,
    ):
        """
        The function is responsible for resetting the client session to its initial
        state. It has two possible ways of resetting the client session:
        1. By explicitly passing a proxies dictionary to the function
            via the proxies parameter. (has precedence over the later)
        2. Pass in a path to a file containing a list of raw and unprocessed proxies.

        Then, we create a new internal session, and chose the set of basic headers
        that is present in the HeaderHelper class. This can be different from the previous one
        if HeaderTools.get_random_user_agent() function is returning a different user agent.

        :param proxies: A dictionary of proxies to apply to the new session
        :param proxy_filename_path: An absolute path to a file containing raw lines of proxies
        :param use_proxies: A boolean that indicates whether the client should use proxies or not.
            **Defaults to True**
        :return:
        """
        pass

    @abstractmethod
    def to_json(self):
        pass

    @abstractmethod
    def from_json(self, data: dict, header_helper: HeaderHelper):
        pass

    @abstractmethod
    def request(
        self,
        method: str,
        url: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        json: Optional[Any] = None,
        timeout: Optional[float] = None,
        proxies: Optional[dict[str, str]] = None,
    ) -> Response:
        pass

    def get(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        """
        :param params: Query parameters to include in the request URL.
        :param data: Data to send in the body of the request (usually for POST/PUT).
        :param headers: Request headers to be included.
        :param cookies: Cookies to include in the request.
        :param json: JSON-serializable object to send as the request body.
        :param timeout: Maximum time to wait for the response, in seconds.
        :param proxies: Proxy mapping used for the request.
        :param verify: Whether to verify the server's TLS certificate.

        :param no_middleware: If True, bypass all middleware logic. This has bigger precedence over the class variable.
        :param use_mitm_when_active: If True, use Man-in-the-Middle (MITM) proxy when active.
            This has bigger precedence over the class variable.

        :param middl_max_retries: Maximum number of retry attempts through middleware.
        :param middl_skip_status_check: If True, skip status code validation logic in middleware.
        :param middl_skip_redirects: If True, bypass redirect-handling logic in middleware.
        :param middl_custom_status_handling_function: Custom callable to handle specific status codes.
            If this is present, then it will be the only function responsible with checking the status code.
        :param middl_redirect_endpoint_stop: If the redirect URL exactly matches this, stop redirect handling.
        :param middl_redirect_endpoint_contains_stop: If the redirect URL contains this substring, stop redirect handling.
        :param middl_statuses_to_skip: List of status codes to skip in middleware status checking.


         :returns: A `Response <Response>` object.
        """
        return self.request(method="GET", url=url, **kwargs)

    def post(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        """
        :param params: Query parameters to include in the request URL.
        :param data: Data to send in the body of the request (usually for POST/PUT).
        :param headers: Request headers to be included.
        :param cookies: Cookies to include in the request.
        :param json: JSON-serializable object to send as the request body.
        :param timeout: Maximum time to wait for the response, in seconds.
        :param proxies: Proxy mapping used for the request.
        :param verify: Whether to verify the server's TLS certificate.

        :param no_middleware: If True, bypass all middleware logic.
        :param use_mitm_when_active: If True, use Man-in-the-Middle (MITM) proxy when active.

        :param middl_max_retries: Maximum number of retry attempts through middleware.
        :param middl_skip_status_check: If True, skip status code validation logic in middleware.
        :param middl_skip_redirects: If True, bypass redirect-handling logic in middleware.
        :param middl_custom_status_handling_function: Custom callable to handle specific status codes.
            If this is present, then it will be the only function responsible with checking the status code.
        :param middl_redirect_endpoint_stop: If the redirect URL exactly matches this, stop redirect handling.
        :param middl_redirect_endpoint_contains_stop: If the redirect URL contains this substring, stop redirect handling.
        :param middl_statuses_to_skip: List of status codes to skip in middleware status checking.


         :returns: A `Response <Response>` object.
        """
        return self.request(method="POST", url=url, **kwargs)

    def put(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        """
        :param params: Query parameters to include in the request URL.
        :param data: Data to send in the body of the request (usually for POST/PUT).
        :param headers: Request headers to be included.
        :param cookies: Cookies to include in the request.
        :param json: JSON-serializable object to send as the request body.
        :param timeout: Maximum time to wait for the response, in seconds.
        :param proxies: Proxy mapping used for the request.
        :param verify: Whether to verify the server's TLS certificate.

        :param no_middleware: If True, bypass all middleware logic.
        :param use_mitm_when_active: If True, use Man-in-the-Middle (MITM) proxy when active.

        :param middl_max_retries: Maximum number of retry attempts through middleware.
        :param middl_skip_status_check: If True, skip status code validation logic in middleware.
        :param middl_skip_redirects: If True, bypass redirect-handling logic in middleware.
        :param middl_custom_status_handling_function: Custom callable to handle specific status codes.
            If this is present, then it will be the only function responsible with checking the status code.
        :param middl_redirect_endpoint_stop: If the redirect URL exactly matches this, stop redirect handling.
        :param middl_redirect_endpoint_contains_stop: If the redirect URL contains this substring, stop redirect handling.
        :param middl_statuses_to_skip: List of status codes to skip in middleware status checking.


         :returns: A `Response <Response>` object.
        """
        return self.request(method="PUT", url=url, **kwargs)

    def delete(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        """
        :param params: Query parameters to include in the request URL.
        :param data: Data to send in the body of the request (usually for POST/PUT).
        :param headers: Request headers to be included.
        :param cookies: Cookies to include in the request.
        :param json: JSON-serializable object to send as the request body.
        :param timeout: Maximum time to wait for the response, in seconds.
        :param proxies: Proxy mapping used for the request.
        :param verify: Whether to verify the server's TLS certificate.

        :param no_middleware: If True, bypass all middleware logic.
        :param use_mitm_when_active: If True, use Man-in-the-Middle (MITM) proxy when active.

        :param middl_max_retries: Maximum number of retry attempts through middleware.
        :param middl_skip_status_check: If True, skip status code validation logic in middleware.
        :param middl_skip_redirects: If True, bypass redirect-handling logic in middleware.
        :param middl_custom_status_handling_function: Custom callable to handle specific status codes.
            If this is present, then it will be the only function responsible with checking the status code.
        :param middl_redirect_endpoint_stop: If the redirect URL exactly matches this, stop redirect handling.
        :param middl_redirect_endpoint_contains_stop: If the redirect URL contains this substring, stop redirect handling.
        :param middl_statuses_to_skip: List of status codes to skip in middleware status checking.


         :returns: A `Response <Response>` object.
        """
        return self.request(method="DELETE", url=url, **kwargs)

    def options(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        """
        :param params: Query parameters to include in the request URL.
        :param data: Data to send in the body of the request (usually for POST/PUT).
        :param headers: Request headers to be included.
        :param cookies: Cookies to include in the request.
        :param json: JSON-serializable object to send as the request body.
        :param timeout: Maximum time to wait for the response, in seconds.
        :param proxies: Proxy mapping used for the request.
        :param verify: Whether to verify the server's TLS certificate.

        :param no_middleware: If True, bypass all middleware logic.
        :param use_mitm_when_active: If True, use Man-in-the-Middle (MITM) proxy when active.

        :param middl_max_retries: Maximum number of retry attempts through middleware.
        :param middl_skip_status_check: If True, skip status code validation logic in middleware.
        :param middl_skip_redirects: If True, bypass redirect-handling logic in middleware.
        :param middl_custom_status_handling_function: Custom callable to handle specific status codes.
            If this is present, then it will be the only function responsible with checking the status code.
        :param middl_redirect_endpoint_stop: If the redirect URL exactly matches this, stop redirect handling.
        :param middl_redirect_endpoint_contains_stop: If the redirect URL contains this substring, stop redirect handling.
        :param middl_statuses_to_skip: List of status codes to skip in middleware status checking.


         :returns: A `Response <Response>` object.
        """
        return self.request(method="OPTIONS", url=url, **kwargs)

    @property
    def cookies(self):
        return self.session.cookies

    @property
    def proxies(self):
        return self.session.proxies

    @property
    def headers(self):
        return self.session.headers

    @proxies.setter
    def proxies(self, new_proxies):
        if not new_proxies:
            return

        if isinstance(new_proxies, str):
            new_proxies = {"http": new_proxies, "https": new_proxies}

        if not new_proxies.get("http") and not new_proxies.get("https"):
            raise ValueError("Proxies must contain an http and https key")

        self.session.proxies = new_proxies

    def copy_essentials(self, other: "Client"):
        self.set_cookies(other.cookies)
        self.set_new_headers(other.headers)
        self.proxies = other.proxies

    def delete_cookies(self, cookies_list: str | list):
        if isinstance(cookies_list, str):
            cookies_list = [cookies_list]

        for cookie in cookies_list:
            del self.cookies[cookie]

    def clear_cookies(self, skip_these: str | list = ""):
        if isinstance(skip_these, str):
            skip_these = [skip_these]

        for cookie in list(self.cookies.keys()):
            if cookie not in skip_these:
                del self.cookies[cookie]

    def _serialize_cookies(self):
        """Serialize the cookies to a list of dictionaries."""
        cookies_list = []
        for cookie in self.cookies:
            cookie_dict = {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": cookie.expires,
                "secure": cookie.secure,
                "rest": cookie._rest,
                "version": cookie.version,
                "port": cookie.port,
                "port_specified": cookie.port_specified,
                "domain_specified": cookie.domain_specified,
                "domain_initial_dot": cookie.domain_initial_dot,
                "path_specified": cookie.path_specified,
                "discard": cookie.discard,
                "comment": cookie.comment,
                "comment_url": cookie.comment_url,
                "rfc2109": cookie.rfc2109,
            }
            cookies_list.append(cookie_dict)
        return cookies_list

    def _deserialize_cookies(self, cookies_list):
        """Deserialize cookies from a list of dictionaries."""
        for cookie_dict in cookies_list:
            cookie = Cookie(
                version=cookie_dict.get("version", 0),
                name=cookie_dict["name"],
                value=cookie_dict["value"],
                port=cookie_dict.get("port"),
                port_specified=cookie_dict.get("port_specified", False),
                domain=cookie_dict.get("domain", ""),
                domain_specified=cookie_dict.get("domain_specified", False),
                domain_initial_dot=cookie_dict.get("domain_initial_dot", False),
                path=cookie_dict.get("path", ""),
                path_specified=cookie_dict.get("path_specified", False),
                secure=cookie_dict.get("secure", False),
                expires=cookie_dict.get("expires"),
                discard=cookie_dict.get("discard", False),
                comment=cookie_dict.get("comment"),
                comment_url=cookie_dict.get("comment_url"),
                rest=cookie_dict.get("rest", {}),
                rfc2109=cookie_dict.get("rfc2109", False),
            )
            self.cookies.set_cookie(cookie)

    def rotate_ip(self, new_proxy: dict = None, proxy_filename_path: str = ""):
        proxies = ""
        if self.proxies:
            retries = 0
            while not proxies and retries < 10:
                proxies = new_proxy or ProxiesHandler.get_proxy(
                    filename=proxy_filename_path
                )
                retries += 1

            self.proxies = proxies
