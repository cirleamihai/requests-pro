import json

from errors.httpErrors import RequestsGroupedError
from requestsClient import RequestsClient
from sessionFactory import SessionFactory
from tlsClient import TLSClient
import sys
from pathlib import Path

from utils.headerTools import HeaderHelper

# @todo: Comment this out in production
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def show_generated_headers():
    # Instantiating a client session will automatically generate headers for you
    requests_client_example = RequestsClient()
    print(requests_client_example.headers)

    """
    will output to this:
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; ARM64; Surface Go 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.84 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, zstd",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Accept-Language": "es-MX;q=0.9, ru-RU;q=0.8, en-GB;q=0.3, es-ES;q=0.2, pt-BR;q=0.2",
        "Sec-GPC": "1",
        "Sec-Ch-Ua": '"Google Chrome";v="128", "Chromium";v="128", "Not)A;Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    }
    """

    # Once we hit this method, the client will reset the headers
    requests_client_example.reset_client()
    print(requests_client_example.headers)

    """
    will output to this:
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; ARM64 Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.114 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, zstd",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Accept-Language": "es-ES;q=0.8, it-IT;q=0.8",
        "Sec-GPC": "1",
        "Sec-Ch-Ua": '"Google Chrome";v="128", "Chromium";v="128", "Not)A;Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
    }
    """

    # Notice how there are different user-agent values that have
    # been generated as well as the accept-language along with other values


def simple_get_request():
    # TLS Client Example
    tls_client_example = TLSClient()
    response = tls_client_example.get("https://httpbin.org/get")
    print(response.status_code, response.text)

    # Once done, you can close the client
    tls_client_example.close()


def simple_post_request():
    # Simple Middlewared Requests Client Example
    requests_client_example = RequestsClient()
    response = requests_client_example.post("https://httpbin.org/post", json={"key": "value"}, data="hey")
    print(response.json())

    # You can reset the client to get new headers
    requests_client_example.reset_client()


def no_request_handler():
    client = TLSClient(no_middleware=True)
    _ = client.get("https://httpbin.org/get?sda", middl_max_retries=22)

    # But later on, if wanted, you can specify for one particular request
    _ = client.get("https://httpbin.org/get?lasd", no_middleware=False)


def advanced_tls_configuration():
    """
    Instantiates TLSClient with advanced TLS parameters to demonstrate flexible configuration.

    In this example, a different client identifier and additional TLS options (like a custom
    JA3 string and HTTP/2 settings) are provided. The response from a GET request is printed,
    and then the session is closed.
    """
    print("Instantiating TLSClient with advanced TLS configuration...")
    client = TLSClient(
        client_identifier="firefox_115",
        ja3_string="771,4865-4867-4866-49195-49196,23-24,0-1-2,29,23",
        h2_settings={"SETTINGS_MAX_CONCURRENT_STREAMS": 100},
        supported_versions=["TLSv1.2", "TLSv1.3"],
        # We also do not want to proxy any requests anymore through charles, even if it's active
        use_mitm_when_active=False
    )
    response = client.get("https://httpbin.org/get")
    print("Advanced TLS config response status:", response.status_code)
    client.close()


def middleware_dealing_with_status_codes():
    """
    Demonstrates custom middleware usage in TLSClient by providing a custom status handling function.

    A simple custom function is defined to treat a 404 status code as acceptable. This function is
    passed via the middl_custom_status_handling_function parameter. A GET request is made to a URL
    that returns 404, and the custom handler's behavior is demonstrated.
    """

    def custom_status_code_handler(resp):
        if resp.status_code == 202:
            raise Exception("This is a custom exception that happens for this status code")

        if resp.status_code != 200:
            # This time, 404 is ok
            if resp.status_code == 404:
                return

            raise Exception(f"Unexpected status code: {resp.status_code}")

    client = RequestsClient(
        # We do not want to proxy any requests anymore through charles, even if it's active
        use_mitm_when_active=False
    )

    # Running this will not show any error
    response = client.get(
        "https://httpbin.org/status/404",
        middl_custom_status_handling_function=custom_status_code_handler
    )
    print(response.status_code)

    # Running this without the custom handler will raise an exception
    # _ = client.get("https://httpbin.org/status/404")

    # Skip the status check
    _ = client.get(
        "https://httpbin.org/status/404",
        middl_skip_status_check=True
    )

    # Skip only some specific status codes when checking the status codes
    _ = client.get(
        "https://httpbin.org/status/404",
        middl_statuses_to_skip=[404, "202"]  # Transforms integers into strings
        # middl_statuses_to_skip=404    # <- This will also work, given it's a single status code
    )


def middleware_in_action():
    client = RequestsClient()

    # Trying to run with very low timeout to trigger a timeout exception
    try:
        client.get("https://httpbin.org/status/404", timeout=0.2)
    except RequestsGroupedError as ex:
        print(ex)

    # Running more than the default max_retries
    try:
        client.get("https://httpbin.org/status/404", middl_max_retries=10, timeout=0.1)
    except RequestsGroupedError as ex:
        print(ex)


def dealing_with_redirects():
    client = TLSClient()

    response = client.get("https://httpbin.org/redirect/2", middl_skip_redirects=True)
    print(response.status_code)  # Will print 302

    response = client.get(
        "https://httpbin.org/redirect/5",
        middl_redirect_endpoint_contains_stop="redirect/2"
    )
    # This will stop once it reaches the endpoint that contains redirect/2
    # In this case, it goes like this:
    # New location: https://httpbin.org/relative-redirect/4  <- Redirect 1
    # New location: https://httpbin.org/relative-redirect/3  <- Redirect 2
    # New location: https://httpbin.org/relative-redirect/2  <- This is where it stops

    print(response.url)

    # Or if you know the exact endpoint to stop at, you can give it like this:

    response = client.get(
        "https://httpbin.org/redirect/5",
        middl_redirect_endpoint_stop="https://httpbin.org/relative-redirect/1"
    )
    # This will stop once it reaches the endpoint that is exactly https://httpbin.org/relative-redirect/1
    # In this case, it goes like this:
    # New location: https://httpbin.org/relative-redirect/4  <- Redirect 1
    # New location: https://httpbin.org/relative-redirect/3  <- Redirect 2
    # New location: https://httpbin.org/relative-redirect/2  <- Redirect 3
    # New location: https://httpbin.org/relative-redirect/1  <- This is where it stops

    print(response.url)


def connection_kept_alive_demo():
    client = TLSClient()
    print("Request 1:")
    client.get("https://httpbin.org/cookies/set?foo=bar")

    print("Request 2 (should reuse session and include cookie):")
    resp = client.get("https://httpbin.org/cookies")
    print(resp.json())  # Should include the cookie set in the first request
    client.close()


def reset_client_breaks_previous_cookies():
    client = TLSClient()
    print("Request 1:")
    client.get("https://httpbin.org/cookies/set?foo=bar")
    client.reset_client()

    print("Request 2 (should be empty):")
    resp = client.get("https://httpbin.org/cookies")
    print(resp.json())  # Should be empty
    client.close()


def header_override_example():
    client = RequestsClient()
    print("Default headers:")
    print(client.headers)

    custom_headers = {
        "User-Agent": "MyCustomAgent/1.0",
        "X-Debug-Token": "abc123"
    }

    print("Request with custom headers:")
    response = client.get("https://httpbin.org/headers", headers=custom_headers)
    print(response.json())  # Should include overridden User-Agent


def proxy_usage_example():
    proxy = {  # This is an example of a proxy configuration
        "http": "http://domain:port[@username:password]",
        "https": "http://domain:port[@username:password]"
    }
    client = TLSClient(proxies=proxy, use_mitm_when_active=False)
    try:
        response = client.get("https://httpbin.org/ip")
        print("Proxy response:", response.json())
    except Exception as e:
        print("Proxy error:", e)
    client.close()


def using_session_factory():
    """
    Create a default RequestsClient using the factory.
    """
    client = SessionFactory.create_client(client_type='requests')
    response = client.get("https://httpbin.org/get")
    print("Response (requests):", response.status_code, response.text)
    print(json.dumps(client.to_json(), indent=2))
    client.close()


def client_with_proxy_file():
    """
    Create a TLSClient using a proxy randomly chosen from a file.
    Assumes the file is in standard proxy format (ip:port or ip:port:user:pass).
    """

    proxy_file = "/your/absolute/path/to/proxies.txt"
    client = SessionFactory.create_client(
        client_type='tls',
        proxy_file_path=proxy_file
    )
    response = client.get("https://httpbin.org/ip")
    print("Proxied IP:", response.json())
    client.close()


def client_with_direct_proxy():
    """
    Create a RequestsClient with a manually provided proxy dictionary.
    """
    proxy_dict = {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080"
    }
    client = SessionFactory.create_client(
        client_type='requests',
        proxy_dict=proxy_dict
    )
    response = client.get("https://httpbin.org/ip")
    print("Proxied IP:", response.json())
    client.close()


def client_with_custom_header_helper():
    """
    Create a TLSClient with a custom HeaderHelper to enforce specific header behavior.
    """

    class MyNewCustomHeaderHelper(HeaderHelper):
        pass

    custom_header_helper = MyNewCustomHeaderHelper()
    client = SessionFactory.create_client(
        client_type='tls',
        header_helper=custom_header_helper
    )

    print("Headers used:", client.headers)
    client.close()


def create_client_from_json():
    json_alike_py_dict = {
        "sessionClientType": "RequestsClient",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6601.2 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, zstd",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Accept-Language": "pt-PT, zh-CN;q=0.6",
            "Sec-GPC": "1",
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"128\", \"Chromium\";v=\"128\", \"Not)A;Brand\";v=\"99\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"macOS\""
        },
        "cookies": [],
        "proxies": {},
        "header_helper": "HeaderHelper",
        "no_middleware": False,
        "use_mitm_when_active": True
    }
    client = SessionFactory.from_json(json_alike_py_dict)
    print("Client created:", client)
    client.get("https://httpbin.org/get")

    print(client.headers)
    client.close()
