import json
import random
from importlib import resources


class UserAgentHandler:
    """
    A utility class to handle the loading and selection of user agent strings
    from a file. User agents are expected to be listed line by line in the file.
    """

    @staticmethod
    def create_user_agent(client_identifier) -> dict:
        """
        Generates a realistic Chrome user agent string along with additional related metadata
        such as the version, platform, and whether it is for a mobile device. The function
        allows for specifying a particular Chrome version or randomly selecting one from the available versions.

        Args:
                client_identifier (str): Optional; specifies a particular Chrome version to use.
                                         If not provided, a random version is selected from the available options.

        Returns:
            dict: A dictionary containing:
                - "user_agent" (str): A complete user agent string formatted for Chrome.
                - "version" (str): The Chrome version number.
                - "platform" (str): The platform on which the browser is running (e.g., "Windows", "macOS", "Android").
                - "mobile" (bool): A boolean indicating whether the user agent is for a mobile device.
        """
        with resources.open_text("requests_pro.files", "chrome_version_info.json") as f:
            version_info = json.load(f)

        with resources.open_text(
            "requests_pro.files", "chrome_subsystem_info.json"
        ) as f:
            subsystem_info = json.load(f)

        if not version_info or not subsystem_info:
            raise ValueError("Not enough data to generate user agent headers.")

        # Getting a version info that our tls client can emulate
        client_identifier = client_identifier or random.choice(
            list(version_info.keys())
        )
        if "chrome" in client_identifier:
            client_identifier = client_identifier.split("chrome_")[1].split("_")[0]

        random_channel = random.choice(list(version_info[client_identifier].keys()))
        random_version = random.choice(version_info[client_identifier][random_channel])
        platform = random_version["platform"]
        random_version = random_version["version"]

        random_subsystem = random.choice(subsystem_info[platform])
        system = random_subsystem["system_info"]
        browser_naming = random_subsystem["browser_naming"]
        end_string = random_subsystem["end_string"]
        webkit_version = "537.36"

        user_agent = (
            f"Mozilla/5.0 ({system}) AppleWebKit/{webkit_version} (KHTML, like Gecko)"
            f" {browser_naming}/{random_version} {end_string}/{webkit_version}"
        )

        return {
            "user_agent": user_agent,
            "version": client_identifier,
            "platform": random_subsystem["platform"],
            "mobile": random_subsystem["mobile"],
        }

    @staticmethod
    def get_user_agent_and_related_headers(client_identifier):
        """
        Constructs a dictionary containing a realistic Chrome user agent string and
        the associated Client Hints headers. These headers include information about the browser version,
        whether the device is mobile, and the platform.

        Args:
                client_identifier (str): Optional; specifies a particular Chrome version to use.
                                         If not provided, a random version is selected from the available options.

        Returns:
            dict: A dictionary containing:
            \n\t    - "user-agent" (str): The user agent string generated by `create_user_agent`.
            \n\t    - "sec-ch-ua" (str): The `sec-ch-ua` header with browser version information.
            \n\t    - "sec-ch-ua-mobile" (str): The `sec-ch-ua-mobile` header, indicating if the device is mobile ("?1" or "?0").
            \n\t    - "sec-ch-ua-platform" (str): The `sec-ch-ua-platform` header indicating the platform (e.g., "Windows", "Linux", "macOS").
        """
        user_agent_info = UserAgentHandler.create_user_agent(client_identifier)
        version = user_agent_info["version"]
        is_mobile = user_agent_info["mobile"]
        platform = user_agent_info["platform"]

        return {
            "Sec-Ch-Ua": f'"Google Chrome";v="{version}", "Chromium";v="{version}", "Not)A;Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?1" if is_mobile else "?0",
            "User-Agent": user_agent_info["user_agent"],
            "Sec-Ch-Ua-Platform": f'"{platform}"',
        }


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # @todo: Comment this out in production
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    with resources.open_text("requests_pro.files", "chrome_version_info.json") as f:
        version_info = json.load(f)

    with resources.open_text("requests_pro.files", "chrome_subsystem_info.json") as f:
        subsystem_info = json.load(f)

    good_version_info = {}
    platforms = []
    for version_number, version_details in version_info.items():
        good_version_info[version_number] = {}
        for channel, versions in version_details.items():
            good_version_info[version_number][channel] = []
            for version in versions:
                platform = version["platform"]
                if platform in subsystem_info:
                    good_version_info[version_number][channel].append(version)
                    if platform not in platforms:
                        platforms.append(platform)

    with open("../files/chrome_version_info.json", "w") as f:
        json.dump(good_version_info, f, indent=4)
