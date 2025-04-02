import random


# noinspection HttpUrlsUsage
class ProxiesHandler:
    """
    A utility class to handle the loading, selection, and formatting of proxy addresses
    from a file. Proxies are expected to be in the format: domain:port[:username:password].
    """

    @staticmethod
    def _load_proxies(filename):
        """
        Loads the list of proxies from the specified file.

        Args:
            filename (str): The name of the file containing the proxies. Defaults to 'proxies.txt'.

        Returns:
            list: A list of proxy strings loaded from the file.
        """
        with open(filename, "r") as file:
            txt_content = file.readlines()
            proxies = []
            for raw_proxy in txt_content:
                proxy = (
                    raw_proxy.strip()
                )  # Remove newline and any surrounding whitespace
                if proxy:
                    proxies.append(proxy)

            return proxies

    @staticmethod
    def _get_raw_proxy(index, filename) -> str:
        """
        Retrieves a raw proxy string from the list by index or randomly if the index is negative.

        Args:
            index (int): The index of the proxy to retrieve. If negative, a random proxy is selected.

        Returns:
            str: The raw proxy string. Returns an empty string if no proxies are available.
        """
        proxies = ProxiesHandler._load_proxies(filename=filename)
        if index >= 0:
            return proxies[index]

        return random.choice(proxies) if proxies else ""

    @staticmethod
    def get_all_proxies(filename: str = "proxies.txt") -> list:
        """
        Loads all proxies from the file and returns a list of formatted proxy strings.
        Args:
            filename (str): The name of the file containing the proxies. Defaults to 'proxies.txt'.
        Returns:
            list: A list of formatted proxy strings in the form 'http://domain:port[@username:password]'.
        """
        # Load the whole proxies first
        proxies = ProxiesHandler._load_proxies(filename=filename)

        # Then return a list of processed proxies
        return [
            ProxiesHandler.get_proxy(proxy=proxy, filename=filename)
            for proxy in proxies
        ]

    @staticmethod
    def get_proxy(
        index: int = -1, proxy: str = None, filename: str = "proxies.txt"
    ) -> str:
        """
        Returns a formatted proxy string in the form 'http://domain:port[@username:password]'.

        Args:
            index: (Optional) the index of the proxy to retrieve. If not provided or negative,
                a random proxy is selected.
            proxy: (Optional) a raw proxy string to format. If provided, the index is ignored.
            filename: (Optional) the name of the file containing the proxies. Defaults to 'proxies.txt'.

        Returns:
            str: The formatted proxy string. Returns an empty string if no valid proxy is available.
        """
        if not proxy:
            proxy = ProxiesHandler._get_raw_proxy(index, filename)

        if not proxy:
            return ""

        proxies_components = proxy.split(":")
        domain = proxies_components[0]
        port = proxies_components[1]
        user_pass = ""

        if len(proxies_components) > 2:
            username = proxies_components[2]
            password = proxies_components[3]
            user_pass += f"{username}:{password}@"

        # Create the proxy URL
        proxy = f"http://{user_pass}{domain}:{port}"
        return proxy

    @staticmethod
    def get_proxy_dict(index: int = -1, filename: str = "proxies.txt") -> dict:
        """
        Returns a dictionary containing the formatted proxy string for both HTTP and HTTPS protocols.

        Args:
            index (int): Optional; the index of the proxy to retrieve. If not provided or negative,
                a random proxy is selected.
            filename (str): Optional; the name of the file containing the proxies. Defaults to 'proxies.txt'.

        Returns:
            dict: A dictionary with 'http' and 'https' keys containing the proxy string.
                  Returns an empty dictionary if no valid proxy is available.
        """
        proxy_str = ProxiesHandler.get_proxy(index, filename=filename)
        if not proxy_str:
            return {}

        return {"http": proxy_str, "https": proxy_str}

    @staticmethod
    def formatted_to_raw_proxy(proxy: str | dict):
        """
        Converts a formatted proxy string or dictionary to a raw proxy string.

        Args:
            proxy (str | dict): The formatted proxy string or dictionary to convert.

        Returns:
            str: The raw proxy string.
        """
        if isinstance(proxy, dict):
            if "http" not in proxy or "https" not in proxy:
                return ""

            proxy = proxy["http"]

        if not proxy.startswith("http://"):
            return ""

        proxy = proxy.replace("http://", "")
        tokens = proxy.split("@")
        if len(tokens) == 1:
            return tokens[0]

        domain = tokens[1].split(":")[0]
        port = tokens[1].split(":")[1]
        user = tokens[0].split(":")[0]
        password = tokens[0].split(":")[1]

        return f"{domain}:{port}:{user}:{password}"
