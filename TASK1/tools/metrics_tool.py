import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "metrics.json"


def get_metrics(
    service: str | None = None,
    incident_id: str | None = None,
) -> list[dict]:
    """
    Retrieve simulated service metrics.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        metrics = json.load(file)

    results = []

    for metric in metrics:
        if service is not None and metric.get("service") != service:
            continue

        if incident_id is not None and metric.get("incident_id") != incident_id:
            continue

        results.append(metric)

    return results