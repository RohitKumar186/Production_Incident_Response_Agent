import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "database.json"


def query_database(
    incident_id: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """
    Retrieve simulated database query information.

    This does not execute a real SQL query.
    It searches the simulated database data.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        database_data = json.load(file)

    results = []

    for record in database_data:
        if incident_id is not None and record.get("incident_id") != incident_id:
            continue

        if status is not None and record.get("status") != status:
            continue

        results.append(record)

    return results