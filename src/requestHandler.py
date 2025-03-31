from http.cookies import SimpleCookie

import requests
from typing import Callable

from tls_client.exceptions import TLSClientExeption

from httpSessions.clientSession import ClientSession
from errors.sessionErrors import *
import urllib3

urllib3.disable_warnings()


class RequestHandler(ClientSession):
    """
    Wraps the client session and adds error handling to the requests.

    Inherits from the ClientSession class in order to be able to use the same interface.
    """

    # noinspection PyMissingConstructor
    def __init__(self, session: ClientSession, **kwargs):
        self.session = session
        self.logger = kwargs['logger']

        self.set_antibot_solvers(**kwargs)

    @staticmethod
    def check_response_status(response: requests.Response, custom_status_handling_function: Callable = None,
                              statuses_to_skip: list = None):
        """
        Checks the response status and raises an error if it is not 200.

        Makes an exception for status code 421, which means redirected for TM.

        In case it needs custom validation for the status code, it will use the custom_handling function.
        """
        if statuses_to_skip and str(response.status_code) in statuses_to_skip:
            return

        if custom_status_handling_function:
            custom_status_handling_function(response)
            return

        if response.status_code != 200:
            if response.status_code == 421 or 400 > response.status_code >= 300:
                return
            elif response.status_code == 403:
                raise AntiBotBlockError(f"Blocked by AntiBot [{response.status_code}]")

            elif response.status_code == 401:
                raise UnauthorizedError(f"Unauthorized [{response.status_code}]", response.text, response)

            elif response.status_code == 404:
                raise NotFoundError(f"Page not found [{response.status_code}]", response.text, response)

            raise requests.exceptions.HTTPError(f"Response status code is not 200 [{response.status_code}]")

    @staticmethod
    def process_kwargs(kwargs: dict):
        """
        Processes the kwargs before passing them to the requests function.
        :param kwargs: the kwargs to process
        """
        # set the default timeout to 20 seconds
        if not kwargs.get('timeout'):
            kwargs['timeout'] = 5

        # do not allow redirects for requests, as we're handling them manually in order to fix the
        # Florian TLS bug that doesn't correctly encode the redirect link
        kwargs['allow_redirects'] = False

        # Skip verifying the SSL certificate by default in order to proxy through Charles
        if kwargs.get('verify', None) is None:
            kwargs['verify'] = False

        statuses_to_skip: list = kwargs.get('statuses_to_skip')
        if statuses_to_skip:
            if isinstance(statuses_to_skip, int) or isinstance(statuses_to_skip, str):
                kwargs['statuses_to_skip'] = [str(statuses_to_skip)]
            else:
                kwargs['statuses_to_skip'] = [str(status) for status in statuses_to_skip]

        del kwargs['method_type']

    @staticmethod
    def _check_for_redirects(response, url: str):
        redirected = False
        if 300 <= response.status_code <= 399:
            url = response.headers.get('Location')
            redirected = True

            if url is None:
                redirected = False

        return url, redirected

    def _set_cookies(self, response):
        """
        Parse the 'Set-Cookie' headers in the response and update the session's cookie jar.

        Args:
            response: The HTTP response object with 'Set-Cookie' headers.

        Example:
            self._set_cookies(response)
        """
        set_cookie_header = response.headers.get('Set-Cookie') or response.headers.get('set-cookie')

        if not set_cookie_header:
            return

        # Check if the header is a single string or a list of cookies
        if isinstance(set_cookie_header, str):
            set_cookie_header = [set_cookie_header]

        for cookie_str in set_cookie_header:
            # Parse each cookie string
            parsed_cookie = SimpleCookie(cookie_str)
            for key, morsel in parsed_cookie.items():
                if not morsel.value:
                    continue

                self.delete_cookies([morsel.key])
                self.set_cookie(name=morsel.key, value=morsel.value, domain=morsel['domain'])

    def _make_request(self, request_method: Callable, url: str, max_retries=3, **kwargs):
        """Wrapper around the request method to handle errors and retries."""
        errors = []
        retries = 0
        skip_status_check = kwargs.pop('skip_status_check', False)
        skip_redirects = kwargs.pop('skip_redirects', False)
        custom_status_handling_function = kwargs.pop('custom_status_handling_function', None)
        redirect_endpoint_stop = kwargs.pop('redirect_endpoint_stop', '')
        redirect_endpoint_contains_stop = kwargs.pop('redirect_endpoint_contains_stop', '')

        # Processing the kwargs before passing them to the requests function
        self.process_kwargs(kwargs)
        statuses_to_skip = kwargs.pop("statuses_to_skip", [])

        while retries < max_retries:
            # if there are any errors, make sure to signal them
            if errors:
                self.logger.error(errors[-1])

            try:
                response = request_method(url, **kwargs)
                self._set_cookies(response)

                # Check for redirects
                url, redirected = self._check_for_redirects(response, url)

                if not skip_status_check:
                    self.check_response_status(response, custom_status_handling_function, statuses_to_skip)

                if (redirected and not skip_redirects and url != redirect_endpoint_stop
                        and not (redirect_endpoint_contains_stop and redirect_endpoint_contains_stop in url)):
                    if 'params' in kwargs: del kwargs['params']
                    continue

                return response

            except requests.exceptions.HTTPError as http_err:
                message = f"HTTP error occurred: {http_err}"
                retries += 1
                errors.append(HTTPError(message))

            except requests.exceptions.ConnectionError as conn_err:
                message = f"Error connecting to the server: {conn_err}"
                retries += 1
                errors.append(ConnectionError(message))

            except requests.exceptions.Timeout as timeout_err:
                message = f"Timeout error: {timeout_err}"
                retries += 1
                errors.append(TimeoutError(message))

            except (requests.exceptions.RequestException, TLSClientExeption) as req_err:
                message = f"An error occurred: {req_err}"
                retries += 1
                errors.append(RequestException(message))

        raise ExceptionGroup(f"Failed to make the request in {max_retries} tries", errors)

    def request(self, method: str, url: str, **kwargs):
        if method == "GET":
            return self.get(url, **kwargs)
        elif method == "POST":
            return self.post(url, **kwargs)
        elif method == "PUT":
            return self.put(url, **kwargs)
        elif method == "DELETE":
            return self.delete(url, **kwargs)
        elif method == "OPTIONS":
            return self.options(url, **kwargs)
        else:
            raise ValueError(f"Invalid method type: {method}")

    def get(self, url: str, **kwargs):
        return self._make_request(self.session.get, url, method_type="GET", **kwargs)

    def post(self, url: str, **kwargs):
        return self._make_request(self.session.post, url, method_type="POST", **kwargs)

    def put(self, url: str, **kwargs):
        return self._make_request(self.session.put, url, method_type="PUT", **kwargs)

    def delete(self, url: str, **kwargs):
        return self._make_request(self.session.delete, url, method_type="DELETE", **kwargs)

    def options(self, url: str, **kwargs):
        return self._make_request(self.session.options, url, method_type="OPTIONS", **kwargs)

    def close(self):
        self.terminate_antibot_sessions()
        self.session.close()

    def set_cookie(self, name, value, domain):
        self.session.set_cookie(name=name, value=value, domain=domain)

    def set_cookies(self, cookies: dict):
        self.session.set_cookies(cookies)

    def delete_cookies(self, cookies_list: str | list):
        self.session.delete_cookies(cookies_list)

    def clear_cookies(self, skip_these: str | list = ""):
        self.session.clear_cookies(skip_these)

    @property
    def headers(self):
        return self.session.headers

    def update_headers(self, new_headers: dict):
        self.session.update_headers(new_headers)

    def set_new_headers(self, new_headers: dict):
        self.session.set_new_headers(new_headers)

    @property
    def cookies(self):
        return self.session.cookies

    @property
    def proxies(self):
        return self.session.proxies

    @proxies.setter
    def proxies(self, value):
        self.session.proxies = value

    def to_json(self):
        json_from_clients = self.session.to_json()
        return {
            **json_from_clients,
            "antibots": self.antibots_to_json()
        }

    @classmethod
    def from_json(cls, **kwargs):
        raise NotImplementedError("This is wrapper class. You cannot create an instance of it.")

    def reset_client(self, reset_antibot_solvers=True):
        self.session.reset_client()

        # Reset the antibot solvers
        if reset_antibot_solvers:
            self.reset_antibot_solvers()

    def copy_essentials(self, other: "RequestHandler"):
        self.session.copy_essentials(other.session)

    def __getattr__(self, name):
        return getattr(self.session, name)
