import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "logs.json"


def search_logs(
    incident_id: str | None = None,
    service: str | None = None,
    level: str | None = None,
    keyword: str | None = None,
) -> list[dict]:
    """
    Search simulated application logs.

    Filters are optional. Multiple filters are combined.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        logs = json.load(file)

    results = []

    for log in logs:
        if incident_id is not None and log.get("incident_id") != incident_id:
            continue

        if service is not None and log.get("service") != service:
            continue

        if level is not None and log.get("level") != level:
            continue

        if keyword is not None:
            message = log.get("message", "").lower()

            if keyword.lower() not in message:
                continue

        results.append(log)

    return results