import json

from config.settings import METRICS_FILE


def read_metrics(service: str):
    """
    Read monitoring metrics for a particular service.
    """

    with open(METRICS_FILE, "r", encoding="utf-8") as file:
        metrics = json.load(file)

    if metrics.get("service") != service:
        return {}

    return metrics