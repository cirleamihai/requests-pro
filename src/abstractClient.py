import random
import socket
from abc import ABC, abstractmethod
from http.cookiejar import Cookie

from database.anonymousConsumables.proxiesHandler import ProxiesHandler
from errors.antibot.antiBotErrors import AntiBotSolverError

from websites.headerHelper import HeaderHelper

# noinspection PyProtectedMember
class Client(ABC):
    """Interface for the client session classes."""

    def __init__(self):
        self.session = None

    @property
    @abstractmethod
    def cookies(self):
        pass

    @property
    @abstractmethod
    def proxies(self):
        pass

    @property
    @abstractmethod
    def headers(self):
        pass

    @abstractmethod
    def update_headers(self, new_headers: dict):
        pass

    @abstractmethod
    def set_new_headers(self, new_headers: dict):
        pass

    @proxies.setter
    @abstractmethod
    def proxies(self, value):
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
    def get(self, url: str, **kwargs):
        pass

    @abstractmethod
    def post(self, url: str, **kwargs):
        pass

    @abstractmethod
    def put(self, url: str, **kwargs):
        pass

    @abstractmethod
    def delete(self, url: str, **kwargs):
        pass

    @abstractmethod
    def options(self, url: str, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def reset_client(self, **kwargs):
        pass

    @abstractmethod
    def to_json(self):
        pass

    @abstractmethod
    def from_json(self, data: dict, header_helper: HeaderHelper):
        pass

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
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires,
                'secure': cookie.secure,
                'rest': cookie._rest,
                'version': cookie.version,
                'port': cookie.port,
                'port_specified': cookie.port_specified,
                'domain_specified': cookie.domain_specified,
                'domain_initial_dot': cookie.domain_initial_dot,
                'path_specified': cookie.path_specified,
                'discard': cookie.discard,
                'comment': cookie.comment,
                'comment_url': cookie.comment_url,
                'rfc2109': cookie.rfc2109,
            }
            cookies_list.append(cookie_dict)
        return cookies_list

    def _deserialize_cookies(self, cookies_list):
        """Deserialize cookies from a list of dictionaries."""
        for cookie_dict in cookies_list:
            cookie = Cookie(
                version=cookie_dict.get('version', 0),
                name=cookie_dict['name'],
                value=cookie_dict['value'],
                port=cookie_dict.get('port'),
                port_specified=cookie_dict.get('port_specified', False),
                domain=cookie_dict.get('domain', ''),
                domain_specified=cookie_dict.get('domain_specified', False),
                domain_initial_dot=cookie_dict.get('domain_initial_dot', False),
                path=cookie_dict.get('path', ''),
                path_specified=cookie_dict.get('path_specified', False),
                secure=cookie_dict.get('secure', False),
                expires=cookie_dict.get('expires'),
                discard=cookie_dict.get('discard', False),
                comment=cookie_dict.get('comment'),
                comment_url=cookie_dict.get('comment_url'),
                rest=cookie_dict.get('rest', {}),
                rfc2109=cookie_dict.get('rfc2109', False),
            )
            self.cookies.set_cookie(cookie)

    def rotate_ip(self):
        proxies = ""
        if self.proxies:
            retries = 0
            while not proxies and retries < 10:
                proxies = ProxiesHandler.get_proxy()
                retries += 1

            self.proxies = proxies
