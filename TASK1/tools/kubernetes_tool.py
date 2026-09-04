import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "kubernetes.json"
)


def get_kubernetes_state(
    service: str | None = None,
) -> dict:
    """
    Retrieve simulated Kubernetes deployment state.
    """

    with DATA_FILE.open("r", encoding="utf-8") as file:
        kubernetes_data = json.load(file)

    deployment = kubernetes_data.get("deployment", {})

    if service is not None and deployment.get("service") != service:
        return {}

    return kubernetes_data