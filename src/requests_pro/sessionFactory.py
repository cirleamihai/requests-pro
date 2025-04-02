from abstractClient import Client
from requestsClient import RequestsClient
from tlsClient import TLSClient
from utils.headerTools import HeaderHelper
from utils.proxiesHandler import ProxiesHandler


class SessionFactory:
    """
    Factory class for creating the client session as well as adding
    the necessary headers, proxies, header helpers and many more.

    The current state of the class doesn't contain a lot of functionality and does not provide an advantage
    over just instantiating the classes directly. But as a project grows, this class is very useful to avoid
    repeating the same code over and over again.

    Keep this in mind if ever forking this project and using it in a bigger project.

    Client Types supported:
    - requests
    - custom TLS client
    """

    @staticmethod
    def from_json(client_dict: dict) -> Client:
        HEADER_HELPER_MAP = {
            "HeaderHelper": HeaderHelper,
        }

        CLIENT_SESSION_MAP = {
            "RequestsClient": RequestsClient,
            "TLSClient": TLSClient,
        }

        header_helper_name = client_dict.get("header_helper")
        header_helper = HEADER_HELPER_MAP.get(header_helper_name)()

        if not header_helper:
            raise ValueError(f"Header helper {header_helper_name} not found.")

        client_type = client_dict.get("sessionClientType")
        client = CLIENT_SESSION_MAP.get(client_type)

        if not client:
            raise ValueError(f"Client session {client_type} not found.")

        return client.from_json(client_dict, header_helper)

    @staticmethod
    def process_client_kwargs(
        proxy_file_path: str,
        proxy_dict: dict,
        header_helper: HeaderHelper,
        kwargs: dict,
    ):
        """
        Processes and stores updated values to the kwargs before using them on instantiations.
        :param proxy_dict: A dictionary of proxies that means running the clients with custom proxies
        :param proxy_file_path: The path to the proxy file
        :param header_helper: The header helper to use in order to deal with automatic header
            handling (user agent, and other headers that need to match across requests)
        :param kwargs: the kwargs to store the processed values
        """
        # Setting up the proxies
        if proxy_file_path or proxy_dict:
            kwargs["proxies"] = proxy_dict or ProxiesHandler.get_proxy_dict(
                proxy_file_path
            )

        # By default, have a random header order option.
        # To prevent detection, each website should have a different class
        kwargs["header_helper"] = header_helper or HeaderHelper()

    @staticmethod
    def create_client(
        client_type: str = "requests",
        proxy_file_path: str = None,
        proxy_dict: dict = None,
        header_helper: HeaderHelper = None,
        no_middleware: bool = False,
        use_mitm_when_active: bool = True,
    ) -> Client:
        kwargs = {}

        # Processing the kwargs
        SessionFactory.process_client_kwargs(
            proxy_file_path,
            proxy_dict,
            header_helper,
            kwargs,
        )

        client_type_map = {
            "requests": RequestsClient,
            "tls": TLSClient,
        }
        client = client_type_map[client_type](
            no_middleware=no_middleware,
            use_mitm_when_active=use_mitm_when_active,
            **kwargs,
        )

        return client
