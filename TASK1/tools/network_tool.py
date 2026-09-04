import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "network.json"


def get_network_metrics(
    service: str | None = None,
    incident_id: str | None = None,
) -> list[dict]:
    """
    Retrieve simulated network metrics.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        network_data = json.load(file)

    results = []

    for record in network_data:
        if service is not None and record.get("service") != service:
            continue

        if incident_id is not None and record.get("incident_id") != incident_id:
            continue

        results.append(record)

    return results