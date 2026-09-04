import json

from config.settings import NETWORK_FILE


def check_network(service: str):
    """
    Read network health information for a service.
    """

    with open(NETWORK_FILE, "r", encoding="utf-8") as file:
        network = json.load(file)

    if network.get("service") != service:
        return {}

    return network