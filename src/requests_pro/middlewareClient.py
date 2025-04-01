import functools
from abc import ABC
from http.cookies import SimpleCookie
from typing import Callable

import requests
import urllib3
from requests import HTTPError, RequestException
from tls_client.exceptions import TLSClientExeption

from abstractClient import Client
from errors.httpErrors import (AntiBotBlockError, NotFoundError,
                                RequestsGroupedError, UnauthorizedError)

urllib3.disable_warnings()


def request_through_middleware(func):
    """
    Decorator function that marks the request as either going through the middleware or not.
    Whenever this decorator is present it marks the fact that the request is going to call the _make_request function.

    :param func: an object's instance that inherits from the MiddlewareClient class
    :return: a function that calls the _make_request function
    """
    @functools.wraps(func)
    def wrapper(self, url: str, *args, **kwargs) -> Callable:
        if kwargs.get("no_middleware"):
            del kwargs["no_middleware"]
            return func(self, url, *args, **kwargs)

        return self._middleware_request(func, url, *args, **kwargs)

    return wrapper


class MiddlewareClient(Client, ABC):
    """
    Acts as a middleware between the Client Interface and the concrete
    implementations of the Interface. It provides an automated way of handling the requests pre- and post-processing.
    """

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
                return  # Ignore these status codes

            elif response.status_code == 403:
                raise AntiBotBlockError(
                    message="Blocked by AntiBot",
                    response_str=response.text,
                    response_obj=response
                )

            elif response.status_code == 401:
                raise UnauthorizedError(
                    message="Unauthorized",
                    response_str=response.text,
                    response_obj=response
                )

            elif response.status_code == 404:
                raise NotFoundError(
                    message="Page not found",
                    response_str=response.text,
                    response_obj=response
                )

            raise requests.exceptions.HTTPError(f"Response status code is not 200 [{response.status_code}]")

    @staticmethod
    def process_kwargs(kwargs: dict):
        """
        Processes the kwargs before passing them to the requests function.
        :param kwargs: the kwargs to process
        """
        # Delete if there is any middleware flag
        kwargs.pop("no_middleware", None)

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

    def _middleware_request(self, request_method: Callable, url: str, max_retries=3, **kwargs):
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
            try:
                response = request_method(self, url, **kwargs)
                self._set_cookies(response)

                # Check for redirects
                url, redirected = self._check_for_redirects(response, url)

                if not skip_status_check:
                    self.check_response_status(response, custom_status_handling_function, statuses_to_skip)

                if (redirected and not skip_redirects and url != redirect_endpoint_stop
                        and not (redirect_endpoint_contains_stop and redirect_endpoint_contains_stop in url)):
                    if 'params' in kwargs:
                        del kwargs['params']
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

        raise RequestsGroupedError(
            f"Failed to make the request in {max_retries} tries", errors
        )
