import json

from config.settings import LOGS_FILE


def search_logs(service: str):
    """
    Search logs belonging to a particular service.
    """

    with open(LOGS_FILE, "r", encoding="utf-8") as file:
        logs = json.load(file)

    matching_logs = [
        log for log in logs
        if log.get("service") == service
    ]

    return matching_logs