import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "deployments.json"
)


def get_deployment_history(
    service: str | None = None,
    version: str | None = None,
) -> list[dict]:
    """
    Retrieve simulated deployment history.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        deployments = json.load(file)

    results = []

    for deployment in deployments:
        if service is not None and deployment.get("service") != service:
            continue

        if version is not None and deployment.get("version") != version:
            continue

        results.append(deployment)

    return results